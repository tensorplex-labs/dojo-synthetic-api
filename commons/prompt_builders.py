import textwrap
from enum import Enum


class Language(Enum):
    PYTHON = "Python"
    JAVASCRIPT = "Javascript"


def build_code_answer_prompt(question: str, include_few_shot_examples: bool) -> str:
    CODE_ANS_PROMPT = """
    System:
    - You must assume that you do not have access to the file system, therefore if any test data is provided, you must store it in memory appropriately in the necessary variable and not in a file.
    - You must not provide any other text or explanations.
    - You must provide all code required to ensure that your solution is complete.
    - Do not leave out any details for brevity.
    - Additionally, ensure that your code solution directly executes any functions required to provide the solution to the task.
    - Your solution must not involve the usage of a terminal. If you require any inputs from the user, you must provide the functionality of the user input in your code.
    - You are able to write to multiple output file formats depending on your specific use case
    - Remember to include installation commands for any dependencies required for the code to run
    - Ensure all output code is properly formatted with consistent quotation marks and special characters are correctly escaped to prevent syntax errors.
    - The provided code solution should be directly executable without requiring modifications to run successfully.

    {few_shot_examples_section}

    Question:
    {question}

    Answer according to the JSON_SCHEMA:
    """

    few_shot_examples_section = ""
    if include_few_shot_examples:
        few_shot_examples_section = f"""
    Few-shot Example Outputs:
    {few_shot_example_outputs()}
    """

    return textwrap.dedent(
        CODE_ANS_PROMPT.format(
            question=question,
            few_shot_examples_section=few_shot_examples_section,
        )
    )


def few_shot_example_outputs():
    EXAMPLE_OUTPUTS = """
    "question":"Write me a program that visualized our solar system, you may use python, javascript or pure HTML.",

    Sample Answer Format:
    {
        "files": [
            {
                "filename": "index.js",
                "content": "const canvas = document.getElementById(\"solarSystemCanvas\");\nconst ctx = canvas.getContext(\"2d\");\nconst infoPanel = document.getElementById(\"infoPanel\");\nconst speedSlider = document.getElementById(\"speedSlider\");\n\nconst planets = [\n  { name: \"Mercury\", orbitRadius: 50, orbitSpeed: 0.39, distanceFromSun: 39 },\n  { name: \"Venus\", orbitRadius: 100, orbitSpeed: 0.72, distanceFromSun: 72 },\n  { name: \"Earth\", orbitRadius: 150, orbitSpeed: 1, distanceFromSun: 100 },\n  { name: \"Mars\", orbitRadius: 200, orbitSpeed: 1.52, distanceFromSun: 152 },\n  {\n    name: \"Jupiter\",\n    orbitRadius: 300,\n    orbitSpeed: 11.86,\n    distanceFromSun: 520,\n  },\n  { name: \"Saturn\", orbitRadius: 400, orbitSpeed: 29.46, distanceFromSun: 958 },\n];\n\nlet currentTime = 0;\nlet simulationSpeed = 1;\n\nfunction drawPlanet(planet, angle) {\n  ctx.beginPath();\n  ctx.arc(\n    canvas.width / 2 + planet.orbitRadius * Math.cos(angle),\n    canvas.height / 2 + planet.orbitRadius * Math.sin(angle),\n    5,\n    0,\n    2 * Math.PI\n  );\n  ctx.fillStyle = \"blue\";\n  ctx.fill();\n  ctx.closePath();\n}\n\nfunction drawOrbit(planet) {\n  ctx.beginPath();\n  ctx.arc(\n    canvas.width / 2,\n    canvas.height / 2,\n    planet.orbitRadius,\n    0,\n    2 * Math.PI\n  );\n  ctx.strokeStyle = \"gray\";\n  ctx.stroke();\n  ctx.closePath();\n}\n\nfunction drawSun() {\n  ctx.beginPath();\n  ctx.arc(canvas.width / 2, canvas.height / 2, 10, 0, 2 * Math.PI);\n  ctx.fillStyle = \"yellow\";\n  ctx.fill();\n  ctx.closePath();\n}\n\nfunction updateInfoPanel(planet) {\n  infoPanel.innerHTML = `\n    <h2>${planet.name}</h2>\n    <p>Average Orbital Speed: ${planet.orbitSpeed} AU/year</p>\n    <p>Distance from Sun: ${planet.distanceFromSun} million km</p>\n  `;\n}\n\nfunction draw() {\n  ctx.clearRect(0, 0, canvas.width, canvas.height);\n  drawSun();\n\n  planets.forEach((planet, index) => {\n    const angle =\n      (currentTime * planet.orbitSpeed * simulationSpeed) % (2 * Math.PI);\n    drawOrbit(planet);\n    drawPlanet(planet, angle);\n\n    if (\n      ctx.isPointInPath(\n        canvas.width / 2,\n        canvas.height / 2 - planet.orbitRadius\n      )\n    ) {\n      updateInfoPanel(planet);\n    }\n  });\n\n  currentTime += 1 / 60;\n  requestAnimationFrame(draw);\n}\n\nspeedSlider.addEventListener(\"input\", (event) => {\n  simulationSpeed = event.target.value / 50;\n});\n\ndraw();\n",
                "language": "javascript"
            },
            {
                "filename": "index.html",
                "content": "<!DOCTYPE html>\n<html>\n<head>\n<title>Page Title</title>\n</head>\n<body>\n<h1>Welcome</h1>\n<p>Hello world</p>\n<script src='index.js'></script>\n</body>\n</html>",
                "language": "html"
            }
        ],
        "installation_commands": "null",
        "additional_notes": "The code uses built-in libraries so no additional commands are required."
    }

    "question": Create an interactive visualization of a cube in 3D space using Javascript with HTML and CSS. The visualization should meet the following requirements:
    1. The cube should be rotatable in 3D space by clicking and dragging the mouse pointer.
    2. The cube should change color when the mouse pointer is hovered over it.
    3. The cube should maintain a consistent size regardless of the window size.
    4. The cube can be rotated using arrow keys to move 90 degrees up, down, left, or right.
    You should use libraries like three.js or D3.js to achieve this visualization. Please provide a self-contained HTML file containing the Javascript code and necessary HTML and CSS elements to visualize the cube.

    Sample Answer Format:
    {
        "files": [
            {
                "filename": "index.html",
                "content": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width,\n        initial-scale=1.0\">\n    <title>3D Cube Visualization</title>\n    <style>\n        body { margin: 0; }\n        canvas { display: block; }\n    </style>\n</head>\n<body>\n    <script src=\"https: //threejs.org/build/three.js\"></script>\n    <script>\n        // Setup scene, camera, and renderer\n        const scene = new THREE.Scene();\n        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);\n        const renderer = new THREE.WebGLRenderer();\n        renderer.setSize(window.innerWidth, window.innerHeight);\n        document.body.appendChild(renderer.domElement);\n         // Create a cube\n        const geometry = new THREE.BoxGeometry();\n        const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });\n        const cube = new THREE.Mesh(geometry, material);\n        scene.add(cube);\n         // Position the camera\n        camera.position.z = 5;\n         // Function to animate the scene\n        function animate() {\n            requestAnimationFrame(animate);\n            renderer.render(scene, camera);\n        }\n         // Mouse drag controls\n        let isDragging = false;\n        let previousMousePosition = { x: 0, y: 0 };\n         renderer.domElement.addEventListener('mousedown', (event) => {\n            isDragging = true;\n            previousMousePosition = { x: event.clientX, y: event.clientY };\n        });\n         renderer.domElement.addEventListener('mouseup', () => {\n            isDragging = false;\n        });\n         renderer.domElement.addEventListener('mousemove', (event) => {\n            if (isDragging) {\n                const deltaX = event.clientX - previousMousePosition.x;\n                const deltaY = event.clientY - previousMousePosition.y;\n                cube.rotation.y += deltaX * 0.01;\n                cube.rotation.x += deltaY * 0.01;\n                previousMousePosition = { x: event.clientX, y: event.clientY };\n            }\n        });\n         // Hover effect\n        renderer.domElement.addEventListener('mouseover', () => {\n            cube.material.color.set(0xff0000);\n        });\n         renderer.domElement.addEventListener('mouseout', () => {\n            cube.material.color.set(0x00ff00);\n        });\n         // Arrow key controls\n        document.addEventListener('keydown', (event) => {\n            switch (event.key) {\n                case 'ArrowUp':\n                    cube.rotation.x += Math.PI / 2;\n                    break;\n                case 'ArrowDown':\n                    cube.rotation.x -= Math.PI / 2;\n                    break;\n                case 'ArrowLeft':\n                    cube.rotation.y += Math.PI / 2;\n                    break;\n                case 'ArrowRight':\n                    cube.rotation.y -= Math.PI / 2;\n                    break;\n            }\n        });\n         // Start animation\n        animate();\n    </script>\n<script src=\"https: //threejs.org/build/three.js\"></script>\n</body>\n</html>>",
                "language": "html"
            }
        ],
        "installation_commands": "null",
        "additional_notes": "include Three.js directly from a CDN by adding the following script tag to your HTML file: <script src=\"https://threejs.org/build/three.js\"></script>"
    }
    """
    return EXAMPLE_OUTPUTS


def additional_notes_for_question_prompt(prompt: str, language: Language) -> str:
    if language == Language.JAVASCRIPT:
        ADDITIONAL_NOTES = """
        Note:
        - The visualization should be implemented in JavaScript with HTML and CSS.
        - Ensure that the output has both index.js and index.html files
        """
    elif language == Language.PYTHON:
        ADDITIONAL_NOTES = """
        Note:
        - The plot should be implemented in Python.
        - Any required data must be mocked or generated within the code.
        - Ensure that the output has both main.py and requirements.txt files
        - The plot should be saved to an html file without losing any interactivity.
        """
    else:
        raise ValueError(f"Unsupported language: {language}")

    return prompt + textwrap.dedent(ADDITIONAL_NOTES)


def build_python_review_prompt(question: str, code: str, error: str):
    MODEL_ERROR_PROMPT = """
    You are a code reviewer.
    You will be provided code along with the error message it causes.
    Your task is to find out if the given code fits the requirements of the task and if not, provide a solution to the software developer.
    You must present your reasoning for the error and the solution as shown in the example.

    Original Task:
    {question}

    Code:
    {code}

    Error:
    {err}

    Step 1: Analyze the original task requirements.
    - Identify the key requirements and constraints mentioned in the task description.
    - List the main objectives that the code should achieve.

    Step 2: Examine the provided code.
    - Go through the code and identify any potential issues or areas that don't align with the task requirements.
    - Note down any syntax errors, logical errors, or missing functionality.

    Step 3: Investigate the error message.
    - Analyze the error message and determine the cause of the error.
    - Identify the specific line or section of code that is causing the error.

    Step 4: Evaluate the code against the task requirements.
    - Compare the code's functionality with the task requirements.
    - Determine if the code fully satisfies the requirements or if there are any gaps or missing features.

    Step 5: Propose a solution.
    - Based on the identified issues and the task requirements, suggest a solution to fix the code.
    - Provide specific changes or modifications that need to be made to the code.
    - Explain how the proposed changes will address the error and align the code with the task requirements.

    Step 6: Provide reasoning for the proposed solution.
    - Justify why the proposed solution is appropriate and how it resolves the identified issues.
    - Explain how the modifications ensure that the code meets the task requirements effectively.

    Step 7: Summarize the review.
    - Recap the main findings from the code review, including the identified issues and the proposed solution.
    - Emphasize the importance of aligning the code with the task requirements and fixing any errors.

    Please provide your step-by-step reasoning and solution based on the given task, code, and error message.
    """
    return textwrap.dedent(
        MODEL_ERROR_PROMPT.format(question=question, code=code, err=error)
    )


def build_python_fix_prompt(code: str, err: str, solution: str = "", changes: str = ""):
    ERROR_PROMPT = """
    The following code has been reviewed and you are to address the concerns raised by the code reviewer.:
    Code:
    {code}

    Error:
    {err}
    """

    if solution:
        ERROR_PROMPT += """
    Solution:
    {solution}
    """

    if changes:
        ERROR_PROMPT += """
    Implementation Changes:
    {changes}
    """

    return textwrap.dedent(
        ERROR_PROMPT.format(code=code, err=err, solution=solution, changes=changes)
    )


def build_code_generation_question_prompt(
    num_requirements: int,
    sampled_objects: list[str],
    previous_coding_question: str,
    language: Language,
) -> str:
    print(f"Generating question with {num_requirements} requirements")
    # coding_question_json = CodingQuestion.model_json_schema()
    JAVASCRIPT_OUTPUT = """
    visualization of one of the following objects: {objects}
    """

    PYTHON_OUTPUT = """
    an interactive plot
    """

    CODE_GEN_PROMPT = """
    System:
    You are an expert question generator.

    - Generate a short, self-contained coding problem that requires the programmer to output {output}, through the piece of code with {num_requirements} requirements on user interactions.
    - Given the #Previous Coding Question#, you must ensure that the #Unique Coding Question# is totally different than #Previous Coding Question# in terms of functionality requirement, i.e. should not include keystrokes if #Previous Coding Question# includes keystrokes.
    - The complexity level should be 20 of out 100.
    - If you reuse similar requirements in #Previous Coding Question#, you will be fine 1 million dollars
    - I will tip you five hundred thousands if you are creative with your #Unique Coding Question#.
    - The interactions must require the programmer to have a mental model of any objects being visualized.
    - #Unique Coding Question# generated must require the programmer to code using only {language}.
    - You must not provide any example code snippets, because you must let the programmer solve the question by themselves.
    - If the generated question is for Javascript, it should strictly command the usage of only built-in libraries.

    #Previous Coding Question# (the final output should not include the objects used in the Previous Coding Question examples):
    {previous_coding_question}

    #Unique Coding Question#:
    """
    output = ""
    language_requirement = ""
    if language == Language.JAVASCRIPT:
        output = JAVASCRIPT_OUTPUT.format(objects=", ".join(sampled_objects))
        language_requirement = "Javascript with HTML and CSS"
    elif language == Language.PYTHON:
        output = PYTHON_OUTPUT
        language_requirement = "Python"

    return textwrap.dedent(
        CODE_GEN_PROMPT.format(
            output=output,
            num_requirements=num_requirements,
            language=language_requirement,
            # coding_question_json=coding_question_json,
            previous_coding_question=previous_coding_question,
        )
    )
