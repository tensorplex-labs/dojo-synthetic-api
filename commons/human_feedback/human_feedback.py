"""
human_feedback.py implements human feedback generation.

incoming HumanFeedbackRequests should trigger generation of hf tasks
- concurrently generate hf tasks for each miner_feedback
- store completed HumanFeedbackResponse in redis
    key: 3 x miner_response_id + validator_task_id?
    value: HumanFeedbackResponse


"""

import random
import uuid
from typing import List

from langfuse.decorators import langfuse_context, observe
from loguru import logger
from tenacity import (
    AsyncRetrying,
    stop_after_attempt,
)

from commons.cache import RedisCache
from commons.config import ANSWER_MODELS
from commons.human_feedback.hf_prompts import get_hf_prompt
from commons.human_feedback.types import (
    GenerateHumanFeedbackPayload,
    HumanFeedbackRequest,
    HumanFeedbackResponse,
    HumanFeedbackTask,
)
from commons.llm import get_llm_api_client
from commons.synthetic import (
    CodeAnswer,
    _get_llm_usage,
    _merge_js_and_html,
    lint_and_fix_code,
)


async def generate_human_feedback(
    hf_request: HumanFeedbackRequest,
) -> HumanFeedbackResponse:
    """
    Driver func to generate human feedback for a given request.
    """
    async_tasks = [
        _generate_human_feedback(
            hf_request.base_prompt,
            hf_request.base_code,
            miner_feedback.feedback,
            miner_feedback.miner_response_id,
        )
        for miner_feedback in hf_request.miner_feedbacks
    ]
    generated_codes = await asyncio.gather(*async_tasks)
    hf_tasks: List[HumanFeedbackTask] = []
    for miner_feedback in hf_request.miner_feedbacks:
        corresponding_code = [
            pair.code
            for pair in generated_codes
            if pair.miner_response_id == miner_feedback.miner_response_id
        ]
        _hf_task = HumanFeedbackTask(
            miner_hotkey=miner_feedback.hotkey,
            feedback=miner_feedback.feedback,
            generated_code=corresponding_code[0],
        )
        hf_tasks.append(_hf_task)

    hf_resp = HumanFeedbackResponse(
        base_prompt=hf_request.base_prompt,
        base_code=hf_request.base_code,
        human_feedback_tasks=hf_tasks,
    )
    # store completed HumanFeedbackResponse in redis
    cache = RedisCache()

    await cache.store_human_feedback(
        hf_request.miner_feedbacks[0].miner_response_id, hf_resp
    )
    return hf_resp


@observe(as_type="generation", capture_input=True, capture_output=True)
async def _generate_human_feedback(
    question: str, answer: str, feedback: str, miner_response_id: str
) -> GenerateHumanFeedbackPayload:
    """
    Generate human feedback for a given question and answer.

    """
    model = random.choice(ANSWER_MODELS)
    client = get_llm_api_client()

    messages = [
        {
            "role": "system",
            "content": get_hf_prompt(question, answer, feedback),
        }
    ]

    kwargs = {
        "response_model": CodeAnswer,
        "model": model,
        "messages": messages,
        "max_retries": AsyncRetrying(stop=stop_after_attempt(2), reraise=True),
        "temperature": 0.0,
    }

    try:
        hf_id = str(uuid.uuid4())
        completion, raw_completion = await client.create_with_completion(**kwargs)
        logger.info(f"generated human feedback: {hf_id}")

        # log to langfuse
        kwargs_clone = kwargs.copy()
        kwargs_clone["response_model"] = kwargs["response_model"].model_json_schema()
        langfuse_context.update_current_observation(
            input=kwargs_clone.pop("messages"),
            model=model,
            output=completion.model_dump(),
            usage=_get_llm_usage(raw_completion),
            metadata={
                "base_prompt": question,
                **kwargs_clone,
            },
        )
        # lint and fix any errors
        completion = await lint_and_fix_code(client, model, completion, hf_id)
        completion = _merge_js_and_html(completion)

        return GenerateHumanFeedbackPayload(
            code=completion, miner_response_id=miner_response_id
        )
    except Exception as e:
        logger.error(f"Error generating human feedback: {hf_id} {e}")
        raise e


async def main():
    """
    for testing human feedback generation. Remove in prod.
    """
    import json
    import os

    from commons.human_feedback.types import MinerFeedback

    logger.info("testing human feedback ...")
    # dummy data
    dummy_prompt = """Create an interactive referee decision simulator that demonstrates nuanced football rules through visual feedback.

Features:
- Display a top-down football field with clearly marked penalty areas and midfield line using HTML canvas
- Implement a referee character that can perform 3 animations: showing yellow card, red card, and pointing for penalty kick
- Create clickable foul zones with different consequences:
  * Penalty area (goalkeeper collision)
  * Midfield (tackle challenge)
  * Wing area (handball scenario)
- Include a severity slider that adjusts from "Incidental Contact" to "Reckless Challenge"
- Add a toggle switch for "Intentional" vs "Unintentional" fouls
- When inputs change, display real-time visual feedback:
  - Field zone highlights with pulsating borders
  - Dynamic text rulings that explain referee's decision logic
  - Animated cards that emerge from referee's pocket with physics-based motion
  - Contextual hand signals that match FIFA officiating standards
- Implement particle effects for card reveals (gold sparkles for yellow, red glow for red)
- Include a "Challenge Flag" button that triggers VAR-style video replay lines over the foul area

User Actions:
1. Click different field zones to simulate foul locations
2. Adjust severity slider to modify foul intensity
3. Toggle intentional/unintentional switch to change foul context

Note: The visualization emphasizes referee decision-making subtleties through interactive elements, mirroring real-world officiating complexities discussed during casual analysis.
Note:
- Your output should be implemented in JavaScript with HTML and CSS.
- Ensure that the output has both index.js and index.html files
"""
    dummy_code = """<!DOCTYPE html>\n\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\"/>\n<meta content=\"width=device-width, initial-scale=1.0\" name=\"viewport\"/>\n<title>Referee Decision Simulator</title>\n<style>\n        body {\n            margin: 0;\n            display: flex;\n            justify-content: center;\n            align-items: center;\n            min-height: 100vh;\n            background: #1a1a1a;\n            font-family: Arial, sans-serif;\n        }\n        #container {\n            position: relative;\n        }\n        canvas {\n            border: 2px solid #444;\n        }\n        .controls {\n            position: absolute;\n            top: 20px;\n            left: 20px;\n            background: rgba(0,0,0,0.7);\n            padding: 15px;\n            border-radius: 8px;\n            color: white;\n        }\n        .var-button {\n            position: absolute;\n            bottom: 20px;\n            right: 20px;\n            padding: 10px 20px;\n            background: #006400;\n            color: white;\n            border: none;\n            border-radius: 4px;\n            cursor: pointer;\n        }\n        .decision-text {\n            position: absolute;\n            top: 20px;\n            right: 20px;\n            color: white;\n            background: rgba(0,0,0,0.7);\n            padding: 10px;\n            border-radius: 4px;\n            max-width: 200px;\n        }\n    </style>\n</head>\n<body>\n<div id=\"container\">\n<canvas id=\"field\"></canvas>\n<div class=\"controls\">\n<div>\n<label>Severity: </label>\n<input id=\"severity\" max=\"100\" min=\"0\" type=\"range\" value=\"50\"/>\n</div>\n<div>\n<label>Intentional: </label>\n<input id=\"intent\" type=\"checkbox\"/>\n</div>\n</div>\n<button class=\"var-button\" id=\"varButton\">VAR Review</button>\n<div class=\"decision-text\" id=\"decisionText\"></div>\n</div>\n<script src=\"index.js\"></script>\n<script>const canvas = document.getElementById('field');\nconst ctx = canvas.getContext('2d');\nconst severitySlider = document.getElementById('severity');\nconst intentCheckbox = document.getElementById('intent');\nconst varButton = document.getElementById('varButton');\nconst decisionText = document.getElementById('decisionText');\n\ncanvas.width = 800;\ncanvas.height = 600;\n\nconst field = {\n    zones: {\n        penaltyArea: { x: 600, y: 200, width: 200, height: 200 },\n        midfield: { x: 300, y: 200, width: 200, height: 200 },\n        wing: { x: 100, y: 100, width: 150, height: 400 }\n    },\n    referee: { x: 400, y: 300, animation: null, card: null },\n    particles: [],\n    varLines: []\n};\n\nfunction drawField() {\n    // Field background\n    ctx.fillStyle = '#2e8b57';\n    ctx.fillRect(0, 0, canvas.width, canvas.height);\n\n    // Field markings\n    ctx.strokeStyle = '#fff';\n    ctx.lineWidth = 2;\n    ctx.strokeRect(50, 50, canvas.width-100, canvas.height-100);\n    ctx.beginPath();\n    ctx.moveTo(canvas.width/2, 50);\n    ctx.lineTo(canvas.width/2, canvas.height-50);\n    ctx.stroke();\n\n    // Penalty areas\n    ctx.strokeRect(50, canvas.height/2-100, 150, 200);\n    ctx.strokeRect(canvas.width-200, canvas.height/2-100, 150, 200);\n}\n\nfunction drawReferee() {\n    ctx.fillStyle = '#000';\n    ctx.beginPath();\n    ctx.arc(field.referee.x, field.referee.y, 10, 0, Math.PI*2);\n    ctx.fill();\n\n    // Animation handling\n    if (field.referee.animation) {\n        const progress = Date.now() - field.referee.animation.start;\n        const duration = 1000;\n        \n        if (progress < duration) {\n            const angle = Math.sin(progress/200) * Math.PI/4;\n            const offsetY = Math.sin(progress/300) * 50;\n            \n            ctx.save();\n            ctx.translate(field.referee.x, field.referee.y);\n            ctx.rotate(angle);\n            \n            // Card drawing\n            ctx.fillStyle = field.referee.card;\n            ctx.fillRect(20, -15 + offsetY, 30, 40);\n            \n            // Particle effects\n            if (Math.random() < 0.3) {\n                field.particles.push({\n                    x: field.referee.x + 35,\n                    y: field.referee.y + offsetY,\n                    color: field.referee.card === 'yellow' ? '#ffd700' : '#ff0000',\n                    velocity: { x: (Math.random()-0.5)*2, y: -Math.random()*3 },\n                    life: 1\n                });\n            }\n            ctx.restore();\n        } else {\n            field.referee.animation = null;\n        }\n    }\n}\n\nfunction updateParticles() {\n    field.particles = field.particles.filter(p => {\n        p.x += p.velocity.x;\n        p.y += p.velocity.y;\n        p.velocity.y += 0.1;\n        p.life -= 0.02;\n        \n        ctx.fillStyle = p.color;\n        ctx.globalAlpha = p.life;\n        ctx.beginPath();\n        ctx.arc(p.x, p.y, 3, 0, Math.PI*2);\n        ctx.fill();\n        \n        return p.life > 0;\n    });\n    ctx.globalAlpha = 1;\n}\n\nfunction determineDecision(zone) {\n    const severity = severitySlider.value/100;\n    const intentional = intentCheckbox.checked;\n    \n    let decision = '';\n    \n    if (zone === 'penaltyArea') {\n        decision = severity > 0.7 ? 'RED CARD + PENALTY' : \n                  intentional ? 'YELLOW CARD + PENALTY' : 'PENALTY';\n    } else if (zone === 'midfield') {\n        decision = severity > 0.6 ? 'RED CARD' :\n                  (severity > 0.3 || intentional) ? 'YELLOW CARD' : 'FOUL';\n    } else if (zone === 'wing') {\n        decision = intentional ? 'YELLOW CARD' : 'FREE KICK';\n    }\n    \n    field.referee.animation = { start: Date.now() };\n    field.referee.card = decision.includes('RED') ? 'red' : \n                        decision.includes('YELLOW') ? 'yellow' : null;\n    \n    decisionText.textContent = `Decision: ${decision}\\n`\n        + `Severity: ${Math.round(severity*100)}%\\n`\n        + `Intent: ${intentional ? 'Deliberate' : 'Accidental'}`;\n}\n\ncanvas.addEventListener('click', (e) => {\n    const rect = canvas.getBoundingClientRect();\n    const x = e.clientX - rect.left;\n    const y = e.clientY - rect.top;\n\n    Object.entries(field.zones).forEach(([zone, area]) => {\n        if (x > area.x && x < area.x + area.width && \n            y > area.y && y < area.y + area.height) {\n            determineDecision(zone);\n            \n            // Zone highlight effect\n            ctx.strokeStyle = '#ff0';\n            ctx.lineWidth = 3;\n            ctx.setLineDash([10, 5]);\n            ctx.strokeRect(area.x, area.y, area.width, area.height);\n            ctx.setLineDash([]);\n        }\n    });\n});\n\nvarButton.addEventListener('click', () => {\n    // VAR line animation\n    field.varLines.push({\n        x1: canvas.width/2, y1: canvas.height/2,\n        x2: field.referee.x, y2: field.referee.y,\n        progress: 0\n    });\n});\n\nfunction animate() {\n    ctx.clearRect(0, 0, canvas.width, canvas.height);\n    drawField();\n    drawReferee();\n    updateParticles();\n    \n    // Animate VAR lines\n    field.varLines = field.varLines.filter(line => {\n        line.progress += 0.02;\n        ctx.strokeStyle = '#fff';\n        ctx.setLineDash([5, 3]);\n        ctx.beginPath();\n        ctx.moveTo(line.x1, line.y1);\n        ctx.lineTo(\n            line.x1 + (line.x2 - line.x1) * line.progress,\n            line.y1 + (line.y2 - line.y1) * line.progress\n        );\n        ctx.stroke();\n        return line.progress < 1;\n    });\n    ctx.setLineDash([]);\n    \n    requestAnimationFrame(animate);\n}\n\nanimate();</script></body>\n</html>"""
    dummy_hf_request = HumanFeedbackRequest(
        base_prompt=dummy_prompt,
        base_code=dummy_code,
        miner_feedbacks=[
            MinerFeedback(
                hotkey="0x1234",
                miner_response_id="1234",
                feedback="Use colour to distinguish between intentional and unintentional fouls",
            )
        ],
    )

    res = await generate_human_feedback(dummy_hf_request)

    # save res to json file
    OUTPUT_FILE = "hf-test.json"
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(CURRENT_DIR, OUTPUT_FILE)
    with open(output_path, "w") as f:
        json.dump(res.model_dump(), f, indent=2)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
