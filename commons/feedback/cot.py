import asyncio

import instructor
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel
from tenacity import AsyncRetrying, RetryError, stop_after_attempt

from commons.llm.openai_proxy import Provider, get_openai_kwargs
from commons.synthetic import log_retry_info

kwargs = get_openai_kwargs(Provider.OPENROUTER)

client = instructor.from_openai(
    AsyncOpenAI(api_key=kwargs["api_key"], base_url=kwargs["base_url"]),
    mode=instructor.Mode.JSON,
)

EXAMPLE_QUESTION = """

Create a Solar System Orbit Simulator using JavaScript, HTML, and CSS. The simulator should display the Sun at the center of the screen and at least 4 planets orbiting around it.

Requirements:
1. Implement a slider that controls the speed of the planets' orbits. The slider should allow users to adjust the simulation speed from very slow to very fast.

2. Add a feature that allows users to click on a planet to display its name and basic information (e.g., size, distance from the Sun) in a small pop-up or sidebar.

3. Include a button that toggles the visibility of planet orbit paths. When enabled, it should show the elliptical paths of the planets' orbits.

Ensure that the planets' sizes and distances are proportional (though not necessarily to scale) to represent the relative differences in the solar system. Use only built-in JavaScript libraries and features for this implementation.
Note:
- The visualization should be implemented in JavaScript with HTML and CSS.
- Ensure that the output is a single index.html file, where any Javascript code is included directly within <script> tags in the HTML, and all CSS is included within <style> tags.

"""


# ORIGINAL PROMPT
# ORIGINAL PROMPT
# Given the following problem statement, provide a detailed step by step plan on how to solve the problem.

# 1. You should first understand the problem statement and the requirements.
# 2. You should then break down the problem into smaller sub-problems in order to iteratively build the program.

PLANNING_PROMPT = ""

PROMPT_1 = f"""
Given the following task, break down the task into core components, then provide a detailed step by step on how the requirements per component.



2. You should then break down the problem into smaller sub-problems in order to iteratively build the program.

When given a complex task or problem to solve, follow these steps:

1. Analyze the task and translate the requirements into core components.

Break down the task into its core components
Identify any constraints or requirements
Determine the key objectives


Generate a high-level plan:

Outline the main steps needed to complete the task
Estimate the time or resources required for each step
Identify any potential challenges or roadblocks


Present the plan:

Summarize your analysis and proposed plan
Explain your reasoning for the chosen approach
Highlight any assumptions you've made


Seek feedback:

Ask if the user wants to modify or approve the plan
Be open to adjusting the plan based on user input


Execute the plan:

Once approved, proceed with implementing the plan step by step
Provide updates on progress at logical checkpoints
Adapt the plan if unexpected issues arise during execution


Conclude:

Summarize the completed task and its outcomes
Reflect on the effectiveness of the plan
Suggest any improvements for future similar tasks



Always prioritize safety, ethics, and the user's best interests throughout the planning and execution process.

Problem Statement:
{EXAMPLE_QUESTION}
"""

PROMPT_2_ORIGINAL = """
System: You are an AI Coding assistant capable of generating complete, fully-functional web-based applications. When asked to create a tetris game, you should provide a full implementation using HTML, JavaScript, and CSS without any external dependencies or libraries. Your response should include:

A fully functional Tetris game with the following features:

Basic sounds and animations
Scoring system
Levels with increasing difficulty
Game over screen when pieces reach the top, displaying the final score with an animation
Keyboard controls using arrow keys and spacebar


The game must run in a web browser without requiring any external files or dependencies.
All game elements, including graphics and sounds, must be generated within the provided code.
The code should be complete and ready to run without any modifications from the user, other than copying and pasting into appropriate HTML, JS, and CSS files.
If the generated code is longer than a single response, break it into sections and ask the user to type "continue" to receive the next part until all code has been provided.
Anticipate and address common bugs or issues in Tetris implementations to ensure a smooth user experience.
Include additional cool features that enhance the Tetris experience without conflicting with the core requirements.
Provide clear instructions on how to run the game in a web browser.
Ensure the code is robust, well-commented, and follows best practices for web development.

"""

GAMING_GENERAL_PROMPT = """
System: You are a capable AI coding assistant capable of generating complete, functional web-based applications. When asked to create an application, you should provide a full implementation using HTML, JavaScript, and CSS, where any external dependencies or libraries may be used using CDNs. Your response should include:

1. A fully functional application with the following features:

- Explicit to the user with all controls available or needed to interact with the application. For this you may use a toast message, for example: use <Space> to jump, <Left> to move left, <Right> to move right, and <Down> to move down.
- Appropriate game speed, for example for a game like tetris the speed of the falling blocks should be slow enough for humans, but not too slow such that it is too easy.
- Scoring or progression system.
- Game over condition and end screen displaying final score or results.
- Suitable controls (for example keyboard, mouse, or touch) for the game type.
- Appropriate graphics and animations for the game type to add interactivity.


2. The game must run in a web browser.
3. If additional dependencies are needed, make sure to use the CDN of the library, for example to use threejs, use <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/<library_version_number>/three.min.js"></script> inside the <head> tag.
4. All application components must be generated within the provided code.
5. The code should be complete and ready to run without any modifications from the user, other than copying and pasting into appropriate HTML, JS, and CSS files.
6. Anticipate and address common bugs or issues in the specific game type to ensure a smooth user experience.
7. If possible, include additional features that enhance the game experience without conflicting with the core requirements.
8. Ensure the code is robust and follows best practices for web development.
9. If the generated code is longer than a single response, break it into sections and ask the user to type "continue" to receive the next part until all code has been provided.
10. Ensure that if the application requires input from the user, the application only starts after user input has been provided before starting.

Remember, you must provide all the code for the application.
This means instead using <link rel="stylesheet" href="styles.css">, you should use <style> tags, like:
<style>
body {
    ...
}
</style>
This means that instead of <script src="script.js"></script>, you should use <script> tags, like:
<script>
function myComponent() {
    ...
}
function myOtherComponent() {
    ...
}
</script>

Task:
Generate a rubik's cube simulator.
"""


PROMPT = GAMING_GENERAL_PROMPT


class SingleFileSolution(BaseModel):
    filename: str
    content: str
    language: str


class CodeSolution(BaseModel):
    files: list[SingleFileSolution]


async def generate_solution(model: str = "anthropic/claude-3.5-sonnet"):
    messages = [
        {"role": "system", "content": PROMPT},
        # {"role": "user", "content": EXAMPLE_QUESTION},
        # {"role": "user", "content": "Generate a tetris game"},
    ]

    kwargs = {
        "response_model": SingleFileSolution,
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 16384,
    }
    MAX_RETRIES = 5

    try:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(MAX_RETRIES), before_sleep=log_retry_info
        ):
            with attempt:
                completion: SingleFileSolution = await client.chat.completions.create(
                    **kwargs
                )
            return completion
    except RetryError as e:
        logger.error(f"Failed to generate answer after {MAX_RETRIES} attempts.")
        raise e
    except Exception as e:
        logger.error(f"Error occurred while generating code answer: {e}")
        raise e

    return completion


async def main():
    solution = await generate_solution()
    logger.info(solution)
    # Write the generated solution to index.html
    path = "./commons/code_executor/untrusted/index.html"
    with open(path, "w") as f:
        f.write(solution.content)

    logger.info(f"Solution written to {path}")
    pass


if __name__ == "__main__":
    asyncio.run(main())
