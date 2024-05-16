from dotenv import load_dotenv
import asyncio
from autogen import AssistantAgent, UserProxyAgent
from loguru import logger
from commons.code_diagnostics import CodeDiagnostics
from commons.llm.openai_proxy import (
    Provider,
    get_openai_kwargs,
)
from autogen.code_utils import extract_code
from autogen.cache import Cache

load_dotenv()


def _is_termination_msg(message):
    """Check if a message is a termination message."""
    if isinstance(message, dict):
        message = message.get("content")
        if message is None:
            return False
        return message.rstrip().endswith(EOS_TOKEN)


# TODO specify the model according to build_prompt_responses_pair
def build_autogen_llm_config(
    model_name: str = "meta-llama/llama-3-8b-instruct",
    provider: Provider = Provider.OPENROUTER,
) -> dict:
    llm_config = {
        "config_list": [
            {
                "model": "meta-llama/llama-3-8b-instruct",
                **get_openai_kwargs(provider=Provider.OPENROUTER),
            }
        ],
    }
    return llm_config


EOS_TOKEN = "TERMINATE"
CODE_DONE_TOKEN = "CODING DONE"
CODING_PROMPT = f"""
You are a coding expert.
You will be provided with a piece of code and can get the diagnostic output from a language server protocol (LSP) server, which is one of the functions that you are provided with.
Your task is to fix the code based on the diagnostics, which will show you errors & warnings in the code.
When the code has no errors, reply with {CODE_DONE_TOKEN}.
You must maintain the original functionality and structure of the code.
You must not omit any details for brevity.
"""
AGENT_CODER_NAME = "coding expert"
# this seems to make the agent worse
# assistant.register_for_llm(
#     name="code_diagnostics",
#     description="Get code diagnostics from a Language Server Protocol (LSP)",
# )(diagnostics_quicklint)

EXTRACT_PROMPT = f"""
Given the corrected code output, you must extract only the code from the following text, up to the {CODE_DONE_TOKEN} token that marks the end of the code output.
You must not include any other text.
You must not change the code in any way.
You must not omit any details for brevity.
"""

# NOTE unused for now due to weird tokens
# groupchat = GroupChat(
#     agents=[user_proxy, coder, reviewer],
#     messages=[],
#     max_round=12,
#     allow_repeat_speaker=False,
# )
# manager = GroupChatManager(groupchat=groupchat, llm_config=build_autogen_llm_config())


def has_code(message):
    if not message:
        return False
    code_blocks = extract_code(message)
    for lang, code in code_blocks:
        if lang.lower() in ["bash", "shell", "sh", "python", "javascript"]:
            return True
    return False


# TODO use model as param
async def fix_code(code: str):
    coder = AssistantAgent(
        AGENT_CODER_NAME,
        system_message=CODING_PROMPT,
        llm_config=build_autogen_llm_config(),
    )

    reviewer = AssistantAgent(
        "code reviewer",
        description=f"Code Reviewer, reviews written code for correctness. Does not do any coding and instead asks the {AGENT_CODER_NAME} to address issues.",
        code_execution_config=False,
        is_termination_msg=_is_termination_msg,
        system_message=f"""
        You are code reviewer.
        Your task is to continuously run diagnostics on the code provided until it has no errors or warnings in order to review the code.
        You will be able to get the code diagnostics from the functions provided.
        You must not do any coding, and must instead delegate the coding tasks to the {AGENT_CODER_NAME}.
        """,
        llm_config=build_autogen_llm_config(),
    )
    reviewer.register_for_execution(name="code_diagnostics")(
        CodeDiagnostics.diagnostics
    )

    user_proxy = UserProxyAgent(
        "UserProxy",
        code_execution_config=False,
        is_termination_msg=_is_termination_msg,
        system_message=f"""
        You are code reviewer.
        Your task is to continuously run diagnostics on the code provided until it has no errors or warnings in order to review the code.
        You will be able to get the code diagnostics from the functions provided.
        You must not do any coding, and must instead delegate the coding tasks to the {AGENT_CODER_NAME}.
        """,
        default_auto_reply="Reply TERMINATE when the initial request has been fulfilled.",
        human_input_mode="NEVER",
    )
    user_proxy.register_for_execution(name="code_diagnostics")(
        CodeDiagnostics.diagnostics
    )

    # with Cache.disk() as cache:
    chat_result = await user_proxy.a_initiate_chat(
        coder,
        message=f"Evaluate and fix the code provided:\n{code}",
        # cache=cache,
    )
    logger.info("Conversation ENDED")

    for message in reversed(chat_result.chat_history):
        if message["role"] == "user" and has_code(message["content"]):
            updated_code = extract_code(message["content"])
            if updated_code:
                logger.success("Successfully parsed code")
                return updated_code
    return None, None


if __name__ == "__main__":
    js_code = """
const canvas = document.getElementById("solarSystemCanvas");
const ctx = canvas.getContext("2d");
const infoPanel = document.getElementById("infoPanel");
const speedSlider = document.getElementById("speedSlider");

const planets = [
{ name: "Mercury", orbitRadius: 50, orbitSpeed: 0.39, distanceFromSun: 39 },
{ name: "Venus", orbitRadius: 100, orbitSpeed: 0.72, distanceFromSun: 72 },
{ name: "Earth", orbitRadius: 150, orbitSpeed: 1, distanceFromSun: 100 },
{ name: "Mars", orbitRadius: 200, orbitSpeed: 1.52, distanceFromSun: 152 },
{
name: "Jupiter",
orbitRadius: 300,
orbitSpeed: 11.86,
distanceFromSun: 520,
},
{ name: "Saturn", orbitRadius: 400, orbitSpeed: 29.46, distanceFromSun: 958 },
];

let currentTime = 0;
let simulationSpeed = 1;

function drawPlanet(planet, angle) {
ctx.beginPath();
ctx.arc(
canvas.width / 2 + planet.orbitRadius * Math.cos(angle),
canvas.height / 2 + planet.orbitRadius * Math.sin(angle),
5,
0,
2 * Math.PI
);
ctx.fillStyle = "blue";
ctx.fill();
ctx.closePath();
}

function drawOrbit(planet) {
ctx.beginPath();
ctx.arc(
canvas.width / 2,
canvas.height / 2,
planet.orbitRadius,
0,
2 * Math.PI
);
ctx.strokeStyle = "gray";
ctx.stroke();
ctx.closePath();
}

function drawSun() {
ctx.beginPath();
ctx.arc(canvas.width / 2, canvas.height / 2, 10, 0, 2 * Math.PI);
ctx.fillStyle = "yellow";
ctx.fill();
ctx.closePath();
}

function updateInfoPanel(planet) {
infoPanel.innerHTML = `
<h2>${planet.name}</h2>
<p>Average Orbital Speed: ${planet.orbitSpeed} AU/year</p>
<p>Distance from Sun: ${planet.distanceFromSun} million km</p>
`;
}

function draw() {
ctx.clearRect(0, 0, canvas.width, canvas.height);
drawSun();

planets.forEach((planet, index) => {
const angle =
(currentTime * planet.orbitSpeed * simulationSpeed) % (2 * Math.PI);
drawOrbit(planet);
drawPlanet(planet, angle);

if (
ctx.isPointInPath(
canvas.width / 2,
canvas.height / 2 - planet.orbitRadius
)
) {
updateInfoPanel(planet);
}
});

currentTie += 1 / 60;
requestAnimationFrame(draw);
}

speedSlider.addEventListener("input", (event => {
simulationSpeed = event.target.value / 50;
});

draw();
    """
    asyncio.run(fix_code(js_code))
