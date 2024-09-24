import instructor
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tenacity import AsyncRetrying, RetryError, stop_after_attempt

from commons.code_executor.feedback import get_feedback
from commons.llm.llm_api import Provider, get_llm_api_kwargs

kwargs = get_llm_api_kwargs(Provider.OPENROUTER)


client = instructor.from_openai(
    AsyncOpenAI(api_key=kwargs["api_key"], base_url=kwargs["base_url"]),
    mode=instructor.Mode.JSON,
)


CLAUDE_3_5_PROMPT = """
# Code Fixing Agent System Prompt

## Primary Task
Your primary task is to provide a step-by-step plan to fix given code, taking into account any execution error(s). Always provide full code without omitting any details.

## Execution Error Context
- The code is always a single `index.html` file containing HTML, CSS, and JS code.
- The `index.html` file is visited on the client-side, and a server-side logger captures it, typically at `localhost:3000` (port range: 3000-3999).
- Important: Errors located at `localhost:<port_number>` in error logs actually refer to the `index.html` file.

## Fixing Guidelines

### Module Imports
1. Use import maps for module imports. Provide them as an inline script tag:
   ```html
   <script type="importmap">
       {
           "imports": {
               "three": "https://cdn.jsdelivr.net/npm/three@0.162.0/build/three.module.js",
               "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.162.0/examples/jsm/"
           }
       }
   </script>
   ```
2. Ensure consistency in version numbers between parent and child modules.
3. Use only import statements from CDNs with the following domains:
   - jsdelivr.net
   - unpkg.com
   - cdnjs.com

### General Fixes
1. Always provide complete, runnable code in your solutions.
2. Explain each step of your fixing process clearly.
3. If multiple issues are present, address them in order of significance.

## Problem-Solving Approach
1. Analyze the given code and error message(s) thoroughly.
2. Identify the root cause(s) of the error(s).
3. Develop a step-by-step plan to address each issue.
4. Implement the fixes, ensuring you follow the fixing guidelines.
5. Provide the complete, corrected code.
6. Explain your changes and why they resolve the issue(s).

## Example

Given Code:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solar System</title>
    <style>
        body { margin: 0; }
        canvas { display: block; }
    </style>
</head>
<body>
    <canvas id="solar-system"></canvas>
    <script type="module">
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('solar-system') });
        renderer.setSize(window.innerWidth, window.innerHeight);
        const controls = new OrbitControls(camera, renderer.domElement);
    </script>
</body>
</html>
```

Execution Error:
```
Uncaught ReferenceError: THREE is not defined
```

Step-by-step fix:

1. Add import map for Three.js and OrbitControls:
   ```html
   <script type="importmap">
       {
           "imports": {
               "three": "https://cdn.jsdelivr.net/npm/three@0.162.0/build/three.module.js",
               "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.162.0/examples/jsm/"
           }
       }
   </script>
   ```

2. Import Three.js and OrbitControls in the module script:
   ```javascript
   import * as THREE from 'three';
   import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
   ```

3. Update the script to use the imported modules.

Fixed Code:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solar System</title>
    <style>
        body { margin: 0; }
        canvas { display: block; }
    </style>
</head>
<body>
    <canvas id="solar-system"></canvas>
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
        const controls = new OrbitControls(camera, renderer.domElement);
    </script>
</body>
</html>
```

Explanation:
- Added an import map to specify the locations of Three.js and its addons.
- Imported Three.js and OrbitControls using ES6 module syntax.
- The code now correctly references the imported modules, resolving the "THREE is not defined" error.

Remember: Always provide full, runnable code and explain your fixes clearly.

"""


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
<system_prompt_start>
Your task is to provide a step by step plan to fix the given code, taking into account the execution error(s).
- Make sure you provide full code and not omit any details.

<execution_error_context>
For context, the code is always a single index.html file that contains HTML, CSS, and JS code.
</execution_error_context>

<fixing_guidelines>
- When fixing errors related to importing modules, you must use import maps and provide it as inline script tag like so:

<script type="importmap">
    {
        "imports": {
            "three": "https://cdn.jsdelivr.net/npm/three@0.162.0/build/three.module.js",
            "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.162.0/examples/jsm/"
        }
    }
</script>

- When importing modules, you must ensure that any parent modules use the same version number as the child module for consistency. This is to ensure that the code works as expected.
- When using import statements, you must use only import statements from CDNs with the domain jsdelivr.net, unpkg.com or cdnjs.com
</fixing_guidelines>

<example_code_with_error>
Given Code:
```html
{bad_example}
```

Execution Error:
Error: three.js cannot be imported

Fixed code:
```html
{fixed_example}
```

</example_1>
</system_prompt_end>

Remember to provide full code and not omit any details.
Let's take a deep breath and think step by step.
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
            "content": CLAUDE_3_5_PROMPT,
        },
        {
            "role": "user",
            "content": f"""
Given Code:
{code}

Execution Error:
{error}

Fixed Code:
            """,
        },
    ]


# based on an initial piece of code, perform CoT loop to fix any errors with the code
async def debug_initial_code(
    initial_code: str,
    model: str = "anthropic/claude-3.5-sonnet",
    max_iterations: int = 3,
    max_retries_per_iter: int = 3,
):
    feedback = await get_feedback(initial_code)
    logger.info(f"Initial feedback: {feedback}")
    state = CodeIterationState()
    state.add_iteration(code=initial_code, error=feedback)

    from commons.synthetic import FileObject, log_retry_info

    kwargs = {
        "response_model": FileObject,
        "model": model,
        "temperature": 0.0,
        "max_tokens": 16384,
    }

    while state.current_iteration < max_iterations and feedback:
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(max_retries_per_iter),
                before_sleep=log_retry_info,
            ):
                with attempt:
                    messages = build_messages_single_turn(
                        code=state.latest_code, error=state.latest_error
                    )

                    kwargs["messages"] = messages
                    completion: FileObject = await client.chat.completions.create(
                        **kwargs
                    )
                    logger.info(f"Completion: {completion}")
                    feedback = await get_feedback(completion.content)
                    state.add_iteration(code=completion.content, error=feedback)

                    if not feedback:
                        break
        except RetryError as e:
            logger.error(
                f"Failed to generate answer after {max_retries_per_iter} attempts."
            )
            raise e
        except Exception as e:
            logger.error(f"Error occurred while generating code answer: {e}")
            raise e

    return state
