import asyncio

import instructor
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tenacity import AsyncRetrying, RetryError, stop_after_attempt

from commons.code_executor.executor_func import get_feedback
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


EOS_TOKEN = "complete"

THREE_JS_BADEXAMPLE = """
...
    <script type="module">
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('solar-system') });
        renderer.setSize(window.innerWidth, window.innerHeight);

        // Add OrbitControls
        const controls = new OrbitControls(camera, renderer.domElement);
        ...
    </script>
...
"""

THREE_JS_FIXED_IMPORTS_EXAMPLE = """
...
    <script type="importmap">
        {
            "imports": {
                "three": "https://cdn.jsdelivr.net/npm/three@0.162.0/build/three.module.js",
                "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.162.0/examples/jsm/"
            }
        }
    </script>
    <script type="module">
        import * as THREE from 'three';
        import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('solar-system') });
        renderer.setSize(window.innerWidth, window.innerHeight);
        ...
    </script>
...
"""

PROMPT = """
Your task is to fix the code given the following code and the error message & diagnostics.
If there is nothing left to fix, simply output "{EOS_TOKEN}".

Code:
{code}

Error:
{error}

For example to fix import errors, you should only use the import statements from CDNs like <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/<library_version_number>/three.min.js"></script> inside the <head> tag.

You must understand that if CDN script is separated from the functions that imports a library, threejs for example, then the main Javascript tag that contains the functions, logic and components cannot find THREE

```html
{bad_example}
... # other code ...
```

Solution:

```html
<script>
{fixed_example}
... # other code ...
```

Let's take a deep breath and think step by step.
"""


ORBIT_CONTROLS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Solar System Visualization</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #000;
            overflow: hidden;
        }
        #solar-system {
            width: 100vw;
            height: 100vh;
        }
    </style>
</head>
<body>
    <canvas id="solar-system"></canvas>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/controls/OrbitControls.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('solar-system') });
        renderer.setSize(window.innerWidth, window.innerHeight);

        // Add OrbitControls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;

        const sunGeometry = new THREE.SphereGeometry(5, 32, 32);
        const sunMaterial = new THREE.MeshBasicMaterial({ color: 0xffff00 });
        const sun = new THREE.Mesh(sunGeometry, sunMaterial);
        scene.add(sun);

        const planets = [
            { name: 'Mercury', radius: 0.5, distance: 10, color: 0x8a8a8a },
            { name: 'Venus', radius: 0.8, distance: 15, color: 0xe39e1c },
            { name: 'Earth', radius: 1, distance: 20, color: 0x6b93d6 },
            { name: 'Mars', radius: 0.7, distance: 25, color: 0xc1440e },
            { name: 'Jupiter', radius: 2, distance: 35, color: 0xd8ca9d },
            { name: 'Saturn', radius: 1.8, distance: 45, color: 0xead6b8 },
            { name: 'Uranus', radius: 1.3, distance: 55, color: 0xd1e7e7 },
            { name: 'Neptune', radius: 1.2, distance: 65, color: 0x5b5ddf }
        ];

        planets.forEach(planet => {
            const geometry = new THREE.SphereGeometry(planet.radius, 32, 32);
            const material = new THREE.MeshBasicMaterial({ color: planet.color });
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.x = planet.distance;
            scene.add(mesh);
        });

        camera.position.z = 100;

        function animate() {
            requestAnimationFrame(animate);
            planets.forEach((planet, index) => {
                const mesh = scene.children[index + 1];
                mesh.position.x = Math.cos(Date.now() * 0.001 * (1 / planet.distance)) * planet.distance;
                mesh.position.z = Math.sin(Date.now() * 0.001 * (1 / planet.distance)) * planet.distance;
            });
            controls.update(); // Update OrbitControls
            renderer.render(scene, camera);
        }

        animate();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""


class CodeIteration(BaseModel):
    code: str
    error: str | None
    iteration: int
    actions: str = Field(
        description="The actions taken at this iteration to solve the problem."
    )
    thoughts: str = Field(
        description="The thought process on whether the actions taken solved the problem or not."
    )


class CodeIterationState(BaseModel):
    iterations: list[CodeIteration] = []
    current_iteration: int = 0

    def add_iteration(self, code: str, error: str | None = None):
        self.iterations.append(
            CodeIteration(
                code=code,
                error=error,
                iteration=self.current_iteration + 1,
                actions="",
                thoughts="",
            )
        )
        self.current_iteration += 1

    @property
    def latest_code(self) -> str:
        return self.iterations[-1].code if self.iterations else ""

    @property
    def latest_error(self) -> str | None:
        return self.iterations[-1].error if self.iterations else None


def build_messages_single_turn(code, error):
    return [
        {
            "role": "system",
            "content": PROMPT.format(
                EOS_TOKEN=EOS_TOKEN,
                code=code,
                error=error,
                bad_example=THREE_JS_BADEXAMPLE.replace("{", "{{").replace("}", "}}"),
                fixed_example=THREE_JS_FIXED_IMPORTS_EXAMPLE.replace("{", "{{").replace(
                    "}", "}}"
                ),
            ),
        },
    ]


async def code_feedback_loop(
    code: str, model: str = "anthropic/claude-3.5-sonnet"
) -> tuple[CodeIterationState, list[dict[str, str]]]:
    feedback = await get_feedback(code)
    logger.info(f"Initial feedback: {feedback}")
    state = CodeIterationState()
    state.add_iteration(code=code, error=feedback)

    kwargs = {
        "response_model": SingleFileSolution,
        "model": model,
        "temperature": 0.0,
        "max_tokens": 16384,
    }
    MAX_OPENROUTER_RETRIES = 5
    MAX_LOOP_ITERATIONS = 3
    complete = False

    # form initial messages array
    message_history = build_messages_single_turn(
        code=state.latest_code, error=state.latest_error
    )
    logger.debug(f"Chat history: {message_history}")

    while not complete and state.current_iteration < MAX_LOOP_ITERATIONS:
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(MAX_OPENROUTER_RETRIES),
                before_sleep=log_retry_info,
            ):
                with attempt:
                    messages = build_messages_single_turn(
                        code=state.latest_code, error=state.latest_error
                    )

                    kwargs["messages"] = messages
                    completion: CodeIteration = await client.chat.completions.create(
                        **kwargs
                    )
                    logger.info(f"Completion: {completion}")
                    # Assuming the completion contains a flag or content indicating completion
                    if EOS_TOKEN == completion.content.strip():
                        complete = True
                        break

                    # Update state with new code and feedback
                    feedback = await get_feedback(completion.content)
                    state.add_iteration(code=completion.content, error=feedback)
                    # Update messages for the next iteration
                    message_history.extend(messages)
        except RetryError as e:
            logger.error(
                f"Failed to generate answer after {MAX_OPENROUTER_RETRIES} attempts."
            )
            raise e
        except Exception as e:
            logger.error(f"Error occurred while generating code answer: {e}")
            raise e

    return state, message_history


async def main():
    _ = await code_feedback_loop(code=ORBIT_CONTROLS_HTML)


if __name__ == "__main__":
    asyncio.run(main())
