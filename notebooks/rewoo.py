import asyncio
import re
import traceback
from typing import Callable, Iterable, List

import instructor
from dotenv import load_dotenv
from loguru import logger
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel, Field

from commons.code_executor import get_feedback
from commons.config import get_settings
from commons.llm import Provider, _get_llm_api_kwargs, get_llm_api_client
from commons.utils import func_to_pydantic_model, get_function_signature

load_dotenv()


prompt = """For the following task, make plans that can solve the problem step by step. For each plan, indicate \
which external tool together with tool input to retrieve evidence. You can store the evidence into a \
variable #E that can be called by later tools. (Plan, #E1, Plan, #E2, Plan, ...) \
You must ensure reusability by defining similar input variables used across different evidence retrieval steps into a variable #I that can be called by later tools. (Plan, #E1[#I1] Plan, #E2[#I1,#I2], Plan, ...)

Tools can be one of the following:
(1) GetCodeFeedback[input]: Use a live execution environment to get runtime error feedback on the code.
(2) Google[input]: Worker that searches results from Google. Useful when you need to find short
and succinct answers about a specific topic. The input should be a search query.
(3) LLM[input]: A pretrained LLM like yourself. Useful when you need to act with general
world knowledge and common sense. Prioritize it when you are confident in solving the problem
yourself. Input can be any instruction.

For example,
Task: Thomas, Toby, and Rebecca worked a total of 157 hours in one week. Thomas worked x
hours. Toby worked 10 hours less than twice what Thomas worked, and Rebecca worked 8 hours
less than Toby. How many hours did Rebecca work?
Plan: Define the initial variables.
#I1 = 157

Plan: Given Thomas worked x hours, translate the problem into algebraic expressions and solve
with Wolfram Alpha.
#I2 = (2x - 10)
#E1 = WolframAlpha[Solve x + #I2 + (#I2 − 8) = #I1]

Plan: Find out the number of hours Thomas worked.
#E2 = LLM[What is x, given #E1]

Plan: Calculate the number of hours Rebecca worked.
#E3 = Calculator[(2 * #E2 − 10) − 8]

Begin!
Describe your plans with rich details. Each Plan must be followed by only one #E, where one #E may use one or more #I.

Task: {task}"""

# Describe your plans with rich details. Each Plan should be followed by only one #E.

buggy_code = """
<!DOCTYPE html>\n\n<html lang="en">\n<head>\n<meta charset="utf-8"/>\n<meta content="width=device-width, initial-scale=1.0" name="viewport"/>\n<title>Interactive Solar System</title>\n<style>\n        body {\n            margin: 0;\n            overflow: hidden;\n            background-color: #000;\n        }\n        canvas {\n            display: block;\n        }\n        #speedSlider {\n            position: absolute;\n            bottom: 20px;\n            left: 20px;\n            width: 200px;\n        }\n        #instructions {\n            position: absolute;\n            top: 20px;\n            left: 20px;\n            color: white;\n            font-family: Arial, sans-serif;\n            font-size: 14px;\n        }\n    </style>\n</head>\n<body>\n<canvas id="solarSystem"></canvas>\n<input id="speedSlider" max="2" min="0.1" step="0.1" type="range" value="1"/>\n<div id="instructions">Click on a planet to zoom in. Use the slider to adjust speed.</div>\n<script src="index.js"></script>\n<script>const canvas = document.getElementById(\'solarSystem\');\nconst ctx = canvas.getContext(\'2d\');\nconst speedSlider = document.getElementById(\'speedSlider\');\n\ncanvas.width = window.innerWidth;\ncanvas.height = window.innerHeight;\n\nconst centerX = canvas.width / 2;\nconst centerY = canvas.height / 2;\n\nconst sun = {\n    x: centerX,\n    y: centerY,\n    radius: 50,\n    color: \'#FFD700\'\n};\n\nconst planets = [\n    { name: \'Mercury\', color: \'#8B8989\', radius: 10, orbitRadius: 100, angle: 0, speed: 0.02, terrainColor: \'#A9A9A9\' },\n    { name: \'Venus\', color: \'#E6E6FA\', radius: 15, orbitRadius: 150, angle: 0, speed: 0.015, terrainColor: \'#DDA0DD\' },\n    { name: \'Earth\', color: \'#4169E1\', radius: 18, orbitRadius: 200, angle: 0, speed: 0.01, terrainColor: \'#228B22\' },\n    { name: \'Mars\', color: \'#B22222\', radius: 14, orbitRadius: 250, angle: 0, speed: 0.008, terrainColor: \'#8B4513\' }\n];\n\nconst stars = [];\nfor (let i = 0; i < 1000; i++) {\n    stars.push({\n        x: Math.random() * canvas.width,\n        y: Math.random() * canvas.height,\n        radius: Math.random() * 1.5\n    });\n}\n\nlet zoomedPlanet = null;\nlet zoomLevel = 1;\n\nfunction drawStar(star) {\n    ctx.beginPath();\n    ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);\n    ctx.fillStyle = \'white\';\n    ctx.fill();\n}\n\nfunction drawSun() {\n    ctx.beginPath();\n    ctx.arc(sun.x, sun.y, sun.radius, 0, Math.PI * 2);\n    ctx.fillStyle = sun.color;\n    ctx.fill();\n}\n\nfunction drawPlanet(planet) {\n    const x = sun.x + Math.cos(planet.angle) * planet.orbitRadius;\n    const y = sun.y + Math.sin(planet.angle) * planet.orbitRadius;\n\n    ctx.beginPath();\n    ctx.arc(x, y, planet.radius, 0, Math.PI * 2);\n\n    const gradient = ctx.createRadialGradient(x, y, 0, x, y, planet.radius);\n    gradient.addColorStop(0, planet.color);\n    gradient.addColorStop(1, shadeColor(planet.color, -30));\n\n    ctx.fillStyle = gradient;\n    ctx.fill();\n\n    // Day/night cycle\n    ctx.beginPath();\n    ctx.arc(x, y, planet.radius, -Math.PI / 2, Math.PI / 2);\n    ctx.fillStyle = \'rgba(0, 0, 0, 0.5)\';\n    ctx.fill();\n}\n\nfunction drawOrbit(planet) {\n    ctx.beginPath();\n    ctx.ellipse(sun.x, sun.y, planet.orbitRadius, planet.orbitRadius * 0.99, 0, 0, Math.PI * 2);\n    ctx.strokeStyle = \'rgba(255, 255, 255, 0.2)\';\n    ctx.stroke();\n}\n\nfunction drawZoomedPlanet(planet) {\n    ctx.save();\n    ctx.translate(canvas.width / 2, canvas.height / 2);\n    ctx.scale(zoomLevel, zoomLevel);\n    ctx.translate(-canvas.width / 2, -canvas.height / 2);\n\n    const terrainGradient = ctx.createRadialGradient(\n        canvas.width / 2, canvas.height / 2, 0,\n        canvas.width / 2, canvas.height / 2, canvas.width / 4\n    );\n    terrainGradient.addColorStop(0, planet.terrainColor);\n    terrainGradient.addColorStop(1, shadeColor(planet.terrainColor, -30));\n\n    ctx.fillStyle = terrainGradient;\n    ctx.fillRect(0, 0, canvas.width, canvas.height);\n\n    // Add some terrain features\n    for (let i = 0; i < 50; i++) {\n        const x = Math.random() * canvas.width;\n        const y = Math.random() * canvas.height;\n        const radius = Math.random() * 20 + 5;\n\n        ctx.beginPath();\n        ctx.arc(x, y, radius, 0, Math.PI * 2);\n        ctx.fillStyle = shadeColor(planet.terrainColor, Math.random() * 40 - 20);\n        ctx.fill();\n    }\n\n    ctx.restore();\n}\n\nfunction shadeColor(color, percent) {\n    const num = parseInt(color.slice(1), 16);\n    const amt = Math.round(2.55 * percent);\n    const R = (num >> 16) + amt;\n    const G = (num >> 8 & 0x00FF) + amt;\n    const B = (num & 0x0000FF) + amt;\n    return `#${(1 << 24 | R << 16 | G << 8 | B).toString(16).slice(1)}`;\n}\n\nfunction animate() {\n    ctx.clearRect(0, 0, canvas.width, canvas.height);\n\n    stars.forEach(drawStar);\n\n    if (zoomedPlanet) {\n        drawZoomedPlanet(zoomedPlanet);\n    } else {\n        drawSun();\n        planets.forEach(drawOrbit);\n        planets.forEach(drawPlanet);\n    }\n\n    const speed = parseFloat(speedSlider.value);\n    planets.forEach(planet => {\n        planet.angle += planet.speed * speed;\n    });\n\n    if (zoomedPlanet && zoomLevel < 10) {\n        zoomLevel += 0.1;\n    } else if (!zoomedPlanet && zoomLevel > 1) {\n        zoomLevel -= 0.1;\n    }\n\n    requestAnimationFrame(animate);\n}\n\ncanvas.addEventListener(\'click\', (event) => {\n    if (zoomedPlanet) {\n        zoomedPlanet = null;\n    } else {\n        const rect = canvas.getBoundingClientRect();\n        const x = event.clientX - rect.left;\n        const y = event.clientY - rect.top;\n\n        planets.forEach(planet => {\n            const planetX = sun.x + Math.cos(planet.angle) * planet.orbitRadius;\n            const planetY = sun.y + Math.sin(planet.angle) * planet.orbitRadius;\n            const distance = Math.sqrt((x - planetX) ** 2 + (y - planetY) ** 2);\n\n            if (distance <= planet.radius) {\n                zoomedPlanet = planet;\n            }\n        });\n    }\n});\n\nanimate();</script></body>\n</html>
"""


class Tool(BaseModel):
    """
    Represents a tool used in a plan step.
    """

    name: str = Field(
        ...,
        description="The name of the tool used in the step, e.g. Google, LLM, GetCodeFeedback",
    )
    purpose: str = Field(..., description="Purpose of the tool call")


class Execution(BaseModel):
    """
    Represents an execution output from a plan step.
    """

    identifier: str = Field(
        ...,
        description="A unique identifier for the execution output (e.g., '#E1').",
    )
    description: str = Field(
        ..., description="Detailed explanation of the execution output."
    )


class InputReference(BaseModel):
    """
    Represents an input reference for a plan step.
    """

    identifier: str = Field(
        ..., description="A unique identifier for the input reference (e.g., '#I1')."
    )
    refers_to: str = Field(
        ...,
        description="The identifier of the execution output that this input references (e.g., '#E1').",
    )
    description: str = Field(
        ..., description="Detailed explanation of the input reference."
    )


class Step(BaseModel):
    """
    Represents a single step in the plan.
    """

    step_id: int = Field(..., description="The unique idenfier of the step.")
    title: str = Field(..., description="The title of the step.")
    purpose: str = Field(..., description="The purpose of the step.")
    tool: Tool = Field(..., description="The tool used in this step.")
    # can consider these dependencies
    inputs: List[InputReference] | None = Field(
        # None, description="A list of input references this step depends on."
        None,
        description="A list of input references from previous steps that this step depends on.",
    )
    output: Execution | None = Field(
        None, description="The execution output produced by this step."
    )


class Plan(BaseModel):
    """
    Represents the entire plan consisting of multiple steps.
    """

    steps: List[Step] = Field(..., description="A list of all steps in the plan.")


class ReWooStrat(BaseModel):
    task: str
    plan: Plan
    # store the `output` identifiers here, for easy lookups
    results: dict


task = f"let #I1 be the following html: {buggy_code}, \nidentify any existing or potential errors or bugs in the code, fix them and return the fully working code"


async def generate_plan() -> Plan | None:
    try:
        client = get_llm_api_client()
        messages = [{"role": "user", "content": prompt.format(task=task)}]
        completion: Plan = await client.chat.completions.create(
            messages=messages,  # type: ignore
            model="openai/gpt-4-turbo",
            stream=False,
            response_model=Plan,
        )

        logger.debug(f"Generated plan... {completion=}")
        return completion
    except Exception as exc:
        logger.error(f"Error generating plan: {exc}")


async def call_llm(input: str) -> ChatCompletion:
    settings = get_settings()
    client = AsyncOpenAI(
        api_key=settings.llm_api.openrouter_api_key.get_secret_value(),
        base_url=settings.llm_api.openrouter_api_base_url,
    )
    return await client.chat.completions.create(
        messages=[{"role": "user", "content": input}],
        model="openai/gpt-4-turbo",
    )


async def google_search(input: str):
    logger.warning("Google search not implemented yet lol")
    logger.warning(f"Google search input: {input}")
    await asyncio.sleep(7 / 3 - 4 / 3 - 1)
    return ""


def resolve_state_key(value: str, rewoo_strat: ReWooStrat):
    logger.debug(f"Resolving state key for {value=}")

    state_key_pattern = re.compile(r"<state_key>(.*?)<\/state_key>")
    matches: Iterable[str] = state_key_pattern.findall(value)

    unknown_keys = set(matches) - set(rewoo_strat.results.keys())
    if len(unknown_keys) > 0:
        logger.warning(f"State keys that don't exist ... {unknown_keys}")

    for match in matches:
        if match not in rewoo_strat.results:
            continue
        value = value.replace(
            f"<state_key>{match}</state_key>", rewoo_strat.results[match]
        )

    logger.debug(f"Resolved state key for {value=}")

    return value


def map_tool_to_function(tool: Tool):
    if tool.name == "Google":
        return google_search
    elif tool.name == "LLM":
        return call_llm
    elif tool.name == "GetCodeFeedback":
        return get_feedback
    else:
        raise NotImplementedError(f"Tool {tool.name} not implemented")


async def build_function_call(func: Callable, step: Step, rewoo_strat: ReWooStrat):
    logger.info(f"Building tool call for step {step.step_id}")

    state_prompt = ""
    for key, value in rewoo_strat.results.items():
        state_prompt += f"{key}: {value}\n"

    tool_prompt = f"""
    Based on the following function signature, help me build the tool call.
    If the input parameter is present in the "App State" below, you do not need to specify the whole "value" again, just use "<state_key>key</state_key>" as the input, for example: "<state_key>#I1</state_key>"

    App State:
    {state_prompt}

    Function Signature: {get_function_signature(func)}
    Title: {step.title}
    Purpose: {step.purpose}
    """

    # if no results yet, might be the first step
    if len(rewoo_strat.results.items()) == 0:
        tool_prompt += f"""
        Context: {rewoo_strat.task}
        """

    # parallel tool only for gpt-4-turbo tho
    tool_client = instructor.from_openai(  # type: ignore
        AsyncOpenAI(
            **_get_llm_api_kwargs(Provider.OPENROUTER),  # type: ignore
        ),
        mode=instructor.Mode.PARALLEL_TOOLS,
    )

    response_model = func_to_pydantic_model(func)
    logger.debug(f"Inferred JSON schema: {response_model.model_json_schema()}")

    exec_args = await tool_client.chat.completions.create(
        messages=[{"role": "user", "content": tool_prompt}],
        model="openai/gpt-4-turbo",
        response_model=Iterable[response_model],
        max_tokens=8192,
    )

    collected_args = []
    for exec_arg in exec_args:
        logger.debug(f"Got tool call params: {exec_arg} for step {step.tool=}")
        collected_args.append(exec_arg.model_dump())

    logger.debug(f"Collected args: {collected_args}")
    assert len(collected_args) == 1
    return collected_args[0]


async def execute_step(step: Step, rewoo_strat: ReWooStrat):
    has_inputs = step.inputs is not None and len(step.inputs) > 0
    if not has_inputs:
        logger.info(f"Executing step {step.step_id} with no inputs")
        try:
            # resolve inputs
            func = map_tool_to_function(step.tool)
            func_signature = get_function_signature(func)
            logger.info(f"Executing step {step.step_id} with {func_signature}")
            # based on the following step in the plan, determine the input

            exec_kwargs = await build_function_call(func, step, rewoo_strat)

            # resolve kwargs by looking in state, this is because we're having some trouble with LLM truncating the long HTML output
            for key, value in exec_kwargs.items():
                exec_kwargs[key] = resolve_state_key(value, rewoo_strat)

            logger.debug(f"Resolved kwargs: {exec_kwargs}")

            result = await func(**exec_kwargs)
            logger.debug(f"Got result: {result} from tool exec")

            # parse output to string
            exec_output = ""
            if isinstance(result, ChatCompletion):
                exec_output = result.choices[0].message.content
            else:
                exec_output = str(result)

            assert step.output is not None
            rewoo_strat.results[step.output.identifier] = exec_output

        except Exception as exc:
            logger.error(f"Error mapping tool to function: {exc}")

            traceback.print_exc()
            pass
    else:
        logger.info(f"Executing step {step.step_id} with inputs")

    pass


async def main():
    plan = await generate_plan()
    if plan is None:
        raise ValueError("Plan is None")

    # initial results
    results = {"#I1": buggy_code}
    rewoo_strat = ReWooStrat(task=task, plan=plan, results=results)

    sorted_steps = sorted(plan.steps, key=lambda s: s.step_id)
    # TODO supposed to be in parallel
    for step in sorted_steps:
        await execute_step(step, rewoo_strat)

    pass


if __name__ == "__main__":
    asyncio.run(main())


# # ## Solver
# #
# # The solver receives the full plan and generates the final response based on the responses of the tool calls from the worker.

# solve_prompt = """Solve the following task or problem. To solve the problem, we have made step-by-step Plan and \
# retrieved corresponding Evidence to each Plan. Use them with caution since long evidence might \
# contain irrelevant information.

# {plan}

# Now solve the question or task according to provided Evidence above. Respond with the answer
# directly with no extra words.

# Task: {task}
# Response:"""


# def solve(state: ReWOO):
#     plan = ""
#     for _plan, step_name, tool, tool_input in state["steps"]:
#         _results = (state["results"] or {}) if "results" in state else {}
#         for k, v in _results.items():
#             tool_input = tool_input.replace(k, v)
#             step_name = step_name.replace(k, v)
#         plan += f"Plan: {_plan}\n{step_name} = {tool}[{tool_input}]"
#     prompt = solve_prompt.format(plan=plan, task=state["task"])
#     result = model.invoke(prompt)
#     return {"result": result.content}


# # ## Define Graph
# #
# # Our graph defines the workflow. Each of the planner, tool executor, and solver modules are added as nodes.


# def _route(state):
#     _step = _get_current_task(state)
#     logger.info(f"Current step: {_step}")
#     if _step is None:
#         # We have executed all tasks
#         return "solve"
#     else:
#         # We are still executing tasks, loop back to the "tool" node
#         return "tool"


# from langgraph.graph import END, START, StateGraph

# graph = StateGraph(ReWOO)
# graph.add_node("plan", get_plan)
# graph.add_node("tool", tool_execution)
# graph.add_node("solve", solve)
# graph.add_edge("plan", "tool")
# graph.add_edge("solve", END)
# graph.add_conditional_edges("tool", _route)
# graph.add_edge(START, "plan")

# app = graph.compile()

# print(graph)

# app.get_graph().print_ascii()

# for s in app.stream({"task": task}):
#     print(s)
#     print("---")
#     # Print out the final result
#     print(s["solve"]["result"])


# # ## Conclusion
# #
# # Congratulations on implementing ReWOO! Before you leave, I'll leave you with a couple limitations of the current implementation from the paper:
# #
# # 1. If little context of the environment is available, the planner will be ineffective in its tool use. This can typically be ameliorated through few-shot prompting and/or fine-tuning.
# # 2. The tasks are still executed in sequence, meaning the total execution time is impacted by _every_ tool call, not just the longest-running in a given step.

# #
