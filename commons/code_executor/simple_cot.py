import asyncio

import instructor
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tenacity import AsyncRetrying, RetryError, stop_after_attempt

from commons.code_executor.feedback import get_feedback
from commons.llm.openai_proxy import Provider, get_openai_kwargs
from commons.synthetic import log_retry_info

kwargs = get_openai_kwargs(Provider.OPENROUTER)

client = instructor.from_openai(
    AsyncOpenAI(api_key=kwargs["api_key"], base_url=kwargs["base_url"]),
    mode=instructor.Mode.JSON,
)


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
