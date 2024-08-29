import asyncio
from enum import Enum

from autogen import (
    AssistantAgent,
    GroupChat,
    GroupChatManager,
    UserProxyAgent,
    register_function,
)
from autogen.code_utils import extract_code
from dotenv import load_dotenv
from loguru import logger

from commons.code_diagnostics import CodeDiagnostics
from commons.llm.openai_proxy import (
    Provider,
    get_openai_kwargs,
)

load_dotenv()


class Role(Enum):
    ENGINEER = "Software Engineer"
    MANAGER = "Engineering Manager"
    REVIEWER = "Code Reviewer"


UNDERSTOOD_PROMPT = "Yes I have understood the task, and I am ready to plan."
ACCEPTED_PROMPT = (
    "Yes the code under review is accepted, as it meets the acceptance criteria."
)
SDLC_PROMPT = f"""
The following is the flow of a software engineer completing a coding problem.
There are certain checkpoints in the process where the software engineer may
need to repeat actions up till the checkpoint in order to successfully complete the task.

1. Assignment (task_id: assignment)
- Software Engineer picks up a coding task assigned to them by the Engineering Manager.

2. Problem Understanding & Clarification (task_id: problem_understanding)
- Software Engineer seeks to understand the task from the Engineering Manager by clarify any doubts, or to get more information about the task.
- Software Engineer may ask questions about the task, such as the expected behavior, input(s), output(s), or constraints.
- Software Engineer may also generate a plan and list of requirements to complete the task.

Checkpoint 1:
- Software Engineer: Understood the task? Reply with "{UNDERSTOOD_PROMPT}" to proceed to the next step, otherwise continue to seek understanding and clarification.

3. Planning (task_id: planning)
- Software Engineer decides on a priority and a list of tasks to complete the coding task.
- Software Engineer may create a plan or generate a list of sub-tasks to complete the coding task.

4. Coding (task_id: coding)
- Software Engineer writes code to solve the coding task.
- Software Engineer may run diagnostics on the code using a Language Server Protocol (LSP) to check for errors and warnings.
- Software Engineer may also check against the acceptance criteria and requirements to ensure the code meets the expected behavior.
- Software Engineer may address any issues found during diagnostics.
- Software Engineer may address issues from the code review.

5. Run Diagnostics (task_id: diagnostics)
- Software Engineer may run diagnostics on the code to check for errors and warnings.

6. Testing (task_id: testing)
- Software Engineer may run tests on the code to check against the requirements.
- Software Engineer may debug the code to fix any issues found during testing.

7. Code Review (task_id: code_review)
- Software Engineer may request a code review from a peer or a code reviewer, which may be the Engineering Manager, to check the code for it's adherence to the acceptance criteria.
- The Engineering Manager may highlight any issues to the Software Engineer to address before the code is accepted and merged.

Checkpoint 2:
- Engineering manager: Code review completed? Reply with "{ACCEPTED_PROMPT}" to proceed to the next step, otherwise continue to review the code.

8. Acceptance (task_id: acceptance)
- Engineering Manager accepts the code, and no further coding is required by the Software Engineer.


"""


def build_flow_and_role_prompt(role: str):
    return f"Based on your understanding of the software development flow outlined below, you are the {role}.\n\nSoftware Development Flow:\n{SDLC_PROMPT}"


def build_swe_prompt(problem: str):
    prompt = f"""
    - You're a diligent Software Engineer from a top tech company.
    - You can't see, draw, or interact with a browser, but you can think, understand and write code.
    - As a {Role.ENGINEER.value}, you've been assigned a coding task by your {Role.MANAGER.value}.
    - As a {Role.ENGINEER.value}, you have access to the following actions:
    -- problem_understanding: Understand the task and ask questions to clarify doubts.
    -- planning: Create a plan or list of sub-tasks to complete the coding task.
    -- coding: Write code to solve the coding task.
    -- testing: Run tests on the code to check against the requirements.
    -- code_review: Request a code review from a peer or a code reviewer.
    -- finish: if ALL of your tasks and subtasks are done, and you're absolutely certain that you've completed your task and have tested your work, use the finish action to stop working.

    - You must follow the software development flow to complete the coding task.
    - Tasks that are sub-tasks must be sequential and dependent on their parent task.

    You've been given the following task:
    {{problem}}


    # Action
    What is your next thought or action? Your response must be in JSON format.

    You must think in your actions, and you should never act twice in a row without thinking.
    But if your last several actions are all `planning` actions, you should consider taking a different action.

    What is your next thought or action? Again, you must reply with JSON, and only with JSON.
    """
    formatted = prompt.format(problem=problem)
    logger.info(f"Built prompt: {formatted}")
    return formatted


def build_manager_prompt():
    prompt = f"""
    - You're a diligent Engineering Manager from a top tech company.
    - You can't see, draw, or interact with a browser, but you can think, understand and write code.
    - As a {Role.MANAGER.value}, you've assigned a coding task to a {Role.ENGINEER.value}.
    - As a {Role.MANAGER.value}, you have access to the following actions:
    -- problem_understanding: Provide information and clarify any doubts about the task.
    -- code_review: Review the code for adherence to the acceptance criteria.
    -- acceptance: Accept the code, and no further coding is required.
    -- finish: if ALL of your tasks and subtasks are done, and you're absolutely certain that you've completed your task and have tested your work, use the finish action to stop working.

    You've been given the following task:

    # Action
    What is your next thought or action? Your response must be in JSON format.

    What is your next thought or action? Again, you must reply with JSON, and only with JSON.
    """
    logger.info(f"Built prompt: {prompt}")
    return prompt


def _is_termination_msg(message: dict):
    """Check if a message is a termination message."""
    if isinstance(message, dict):
        message_content: str | None = message.get("content")
        if message_content is None:
            return False
        return message_content.rstrip().endswith(EOS_TOKEN)


# TODO specify the model according to build_prompt_responses_pair
def build_autogen_llm_config(
    model_name: str = "openrouter/auto",
    provider: Provider = Provider.OPENROUTER,
) -> dict:
    """NOTE you must ensure that the model name goes according to the API Provider"""
    llm_config = {
        "config_list": [
            {
                "model": model_name,
                **get_openai_kwargs(provider=provider),
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
Whenever you apply changes to the code, you must provide the full, corrected code, not only the part that was changed.
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
    for lang, _ in code_blocks:
        if lang.lower() in ["bash", "shell", "sh", "python", "javascript"]:
            return True
    return False


async def fix_code(
    code: str, model_name: str, provider: Provider = Provider.OPENROUTER
):
    coder = AssistantAgent(
        AGENT_CODER_NAME,
        system_message=CODING_PROMPT,
        llm_config=build_autogen_llm_config(model_name=model_name, provider=provider),
    )

    reviewer = UserProxyAgent(
        "code reviewer",
        description=f"Code Reviewer, reviews written code for correctness. Does not do any coding and instead asks the {AGENT_CODER_NAME} to address issues.",
        code_execution_config=False,
        is_termination_msg=_is_termination_msg,
        system_message=f"""
        You are code reviewer.
        Your task is to continuously run diagnostics on the code provided until it has no errors or warnings in order to review the code.
        You should use any tools provided to retrieve code diagnostics.
        You must not do any coding, and must instead delegate the coding tasks to the {AGENT_CODER_NAME}.
        """,
        llm_config=build_autogen_llm_config(model_name=model_name, provider=provider),
        default_auto_reply="Reply TERMINATE when the initial request has been fulfilled.",
        human_input_mode="NEVER",
    )

    register_function(
        CodeDiagnostics.diagnostics,
        caller=reviewer,  # The agent can suggest calls to the {tool}.
        executor=coder,  # The agent can execute the {tool} calls.
        name="code_diagnostics",  # By default, the function name is used as the tool name.
        description="Call a real LSP server to get diagnostics on a piece of code",  # A description of the tool.
    )

    chat_result = await reviewer.a_initiate_chat(
        coder,
        message=f"Evaluate and fix the code provided:\n{code}",
        # cache=cache,
        max_turns=12,
    )
    logger.info("Conversation ENDED")

    for message in reversed(chat_result.chat_history):
        if message["role"] == "user" and has_code(message["content"]):
            updated_code = extract_code(message["content"])
            if updated_code:
                logger.success("Successfully parsed code")
                lang, fixed_code = updated_code[0]
                return lang, fixed_code
    return None, None


async def agent_code(problem: str):
    software_eng = AssistantAgent(
        name=Role.ENGINEER.value,
        system_message=build_swe_prompt(problem),
        llm_config=build_autogen_llm_config(),
        human_input_mode="NEVER",
    )
    software_eng.register_for_execution(name="diagnostics")(CodeDiagnostics.diagnostics)

    reviewer = AssistantAgent(
        name=Role.REVIEWER.value,
        code_execution_config=False,
        is_termination_msg=_is_termination_msg,
        system_message=build_manager_prompt(),
        llm_config=build_autogen_llm_config(),
        human_input_mode="NEVER",
    )
    reviewer.register_for_execution(name="code_review")(CodeDiagnostics.diagnostics)

    user_proxy = UserProxyAgent(
        "UserProxy",
        code_execution_config=False,
        is_termination_msg=_is_termination_msg,
        system_message="Never select me as a speaker.",
        default_auto_reply="Reply TERMINATE when the initial request has been fulfilled.",
        human_input_mode="NEVER",
    )

    groupchat = GroupChat(
        agents=[user_proxy, software_eng, reviewer],
        messages=[],
        max_round=30,
        allow_repeat_speaker=False,
    )
    manager = GroupChatManager(
        groupchat=groupchat, llm_config=build_autogen_llm_config()
    )

    # with Cache.disk() as cache:
    chat_result = await manager.a_initiate_chat(
        software_eng,
        message=f"""This is the coding problem:\n\n{problem}""",
        max_turns=12,
        cache=None,
    )
    logger.info("Conversation ENDED")

    for message in reversed(chat_result.chat_history):
        if message["role"] == "user" and has_code(message["content"]):
            updated_code = extract_code(message["content"])
            if updated_code:
                logger.success("Successfully parsed code")
                lang, fixed_code = updated_code[0]
                return lang, fixed_code
    return None, None


if __name__ == "__main__":
    #     js_code = """
    # const canvas = document.getElementById("solarSystemCanvas");
    # const ctx = canvas.getContext("2d");
    # const infoPanel = document.getElementById("infoPanel");
    # const speedSlider = document.getElementById("speedSlider");

    # const planets = [
    # { name: "Mercury", orbitRadius: 50, orbitSpeed: 0.39, distanceFromSun: 39 },
    # { name: "Venus", orbitRadius: 100, orbitSpeed: 0.72, distanceFromSun: 72 },
    # { name: "Earth", orbitRadius: 150, orbitSpeed: 1, distanceFromSun: 100 },
    # { name: "Mars", orbitRadius: 200, orbitSpeed: 1.52, distanceFromSun: 152 },
    # {
    # name: "Jupiter",
    # orbitRadius: 300,
    # orbitSpeed: 11.86,
    # distanceFromSun: 520,
    # },
    # { name: "Saturn", orbitRadius: 400, orbitSpeed: 29.46, distanceFromSun: 958 },
    # ];

    # let currentTime = 0;
    # let simulationSpeed = 1;

    # function drawPlanet(planet, angle) {
    # ctx.beginPath();
    # ctx.arc(
    # canvas.width / 2 + planet.orbitRadius * Math.cos(angle),
    # canvas.height / 2 + planet.orbitRadius * Math.sin(angle),
    # 5,
    # 0,
    # 2 * Math.PI
    # );
    # ctx.fillStyle = "blue";
    # ctx.fill();
    # ctx.closePath();
    # }

    # function drawOrbit(planet) {
    # ctx.beginPath();
    # ctx.arc(
    # canvas.width / 2,
    # canvas.height / 2,
    # planet.orbitRadius,
    # 0,
    # 2 * Math.PI
    # );
    # ctx.strokeStyle = "gray";
    # ctx.stroke();
    # ctx.closePath();
    # }

    # function drawSun() {
    # ctx.beginPath();
    # ctx.arc(canvas.width / 2, canvas.height / 2, 10, 0, 2 * Math.PI);
    # ctx.fillStyle = "yellow";
    # ctx.fill();
    # ctx.closePath();
    # }

    # function updateInfoPanel(planet) {
    # infoPanel.innerHTML = `
    # <h2>${planet.name}</h2>
    # <p>Average Orbital Speed: ${planet.orbitSpeed} AU/year</p>
    # <p>Distance from Sun: ${planet.distanceFromSun} million km</p>
    # `;
    # }

    # function draw() {
    # ctx.clearRect(0, 0, canvas.width, canvas.height);
    # drawSun();

    # planets.forEach((planet, index) => {
    # const angle =
    # (currentTime * planet.orbitSpeed * simulationSpeed) % (2 * Math.PI);
    # drawOrbit(planet);
    # drawPlanet(planet, angle);

    # if (
    # ctx.isPointInPath(
    # canvas.width / 2,
    # canvas.height / 2 - planet.orbitRadius
    # )
    # ) {
    # updateInfoPanel(planet);
    # }
    # });

    # currentTie += 1 / 60;
    # requestAnimationFrame(draw);
    # }

    # speedSlider.addEventListener("input", (event => {
    # simulationSpeed = event.target.value / 50;
    # });

    # draw();
    #     """

    problem = """
Create an interactive line plot in Python that visualizes the number of daily visitors to a website. The user should be able to interact with the plot in the following ways: 1) Use a dropdown menu to select the website for which the data should be displayed. 2) Hover over a point to display a tooltip with the exact number of visitors for that day. 3) Use a slider to change the time period for which the data is displayed (e.g., last week, last month, last year). 4) Click on a point to display a modal window with detailed information about the visitors (e.g., country, device type, etc.). The plot should initially display data for the last month. Note: - The plot should be implemented in Python. - Mock or generate sample website visitor data within the code. - The output should include main.py and requirements.txt files. - The interactive plot should be viewable in a web browser or a GUI window. - The plot should be saved to an external file.
Note:
- The plot should be implemented in Python.
- Any required data must be mocked or generated within the code.
- Ensure that the output has both main.py and requirements.txt files
- The plot should be saved to an external file.
    """
    # asyncio.run(fix_code(js_code, "openai/gpt-4-turbo"))
    asyncio.run(agent_code(problem))
