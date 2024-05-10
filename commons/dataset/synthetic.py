import os
import re
import sys
import json
import asyncio
import random
import textwrap
import instructor
from typing import List, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from tenacity import AsyncRetrying, RetryError, stop_after_attempt, wait_fixed

sys.path.append("./")
from commons.llm.openai_proxy import Provider, get_openai_client
from commons.utils.utils import generate_simple_json

load_dotenv()


class CodingQuestion(BaseModel):
    question: str = Field(
        description="Coding question to be solved by a software engineer"
    )


# Schema for the generated coding answer from LLM
class FileObject(BaseModel):
    filename: str = Field(description="Name of the file")
    content: str = Field(description="Content of the file which can be code or json")
    language: str = Field(description="Programming language of the file")


class CodeAnswer(BaseModel):
    files: List[FileObject] = Field(
        description="Array of FileObject, that are part of the code solution. Must include index.html, and index.js a Javascript solution"
    )
    installation_commands: str = Field(
        description="Terminal commands for the code to be able to run to install any third-party packages for the code to be able to run"
    )
    additional_notes: Optional[str] = Field(
        description="Any additional notes or comments about the code solution"
    )


def parse_code_response(result_object: CodeAnswer) -> CodeAnswer:
    """Ensure that necessary files appended for python"""
    result_object = append_codesandbox_files(result_object)
    # result_object = escape_double_quotes_in_files(result_object)
    return result_object


def escape_double_quotes_in_files(codeanswer_object: CodeAnswer) -> CodeAnswer:
    """Escapes double quotes in the content of each file in the CodeAnswer object."""
    for file in codeanswer_object.files:
        if "content" in file.model_dump():
            file.content = re.sub(r'(?<!\\)"', r"\"", file.content)
            file.content = file.content.replace(r"\'", r"'")
    return codeanswer_object


def append_codesandbox_files(codeanswer_object: CodeAnswer) -> CodeAnswer:
    javascript_file_detected = False
    for file in codeanswer_object.files:
        if file.language == "javascript":
            javascript_file_detected = True
            break

    if javascript_file_detected:
        package_json_content = json.dumps(
            {"dependencies": {"three": "latest"}}, indent=4
        )

        package_json_file = FileObject(
            filename="package.json",
            content=package_json_content,
            language="json",
        )
        codeanswer_object.files.append(package_json_file)

    return codeanswer_object


async def generate_question(
    client: instructor.AsyncInstructor, model: str
) -> Optional[str]:
    print(f"Generating question with model: {model}")
    kwargs = {
        "response_model": CodingQuestion,
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": build_code_generation_question_prompt(
                    random.choices([3, 4, 5], weights=[0.5, 0.3, 0.2])[0]
                ),
            }
        ],
        "temperature": random.uniform(0.0, 0.5),
        "max_tokens": 8192,
        "top_p": random.uniform(0.9, 1.0),
        "seed": random.randint(0, 1e9),  # needed for OpenAI
    }
    try:
        completion = await client.chat.completions.create(**kwargs)
        coding_question = completion.question
        coding_question = additional_notes_for_question_prompt(coding_question)
        print(f"Generated question: {coding_question}")
        return coding_question
    except Exception as e:
        print(f"Error occurred while generating question: {e}")
        pass


def build_code_generation_question_prompt(num_requirements: int) -> str:
    print(f"Generating question with {num_requirements} requirements")
    # coding_question_json = CodingQuestion.model_json_schema()
    CODE_GEN_PROMPT = """
    System:
    - Generate a short, self-contained, challenging coding problem that requires the programmer to output an visualization from the piece of code with {num_requirements} requirements on the functionality of the interactions.
    - The interactions must require the programmer to have a mental model of any objects being visualized.
    - The question generated must require the programmer to code using only Javascript with HTML and CSS.
    - You must not provide any example code snippets, because you must let the programmer solve the question by themselves.
    - If the generated question is for Javascript, it should strictly command the usage of only built-in libraries.

    Coding Question:
    """
    return textwrap.dedent(
        CODE_GEN_PROMPT.format(
            num_requirements=num_requirements,
            # coding_question_json=coding_question_json,
        )
    )


def additional_notes_for_question_prompt(prompt: str) -> str:
    ADDITIONAL_NOTES = """
    Note:
    - The visualization should be implemented in JavaScript with HTML and CSS.
    - Ensure that the output has both index.js and index.html files
     """
    return prompt + textwrap.dedent(ADDITIONAL_NOTES)


async def generate_answer(client: AsyncOpenAI, model: str, question: str):
    """Generates a coding question answer for a given coding question."""
    print(f"Generating code answer with model: {model}")
    kwargs = {
        "response_model": CodeAnswer,
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": f"You are an expert at outputting json. You always output valid json based on this schema: {CodeAnswer.model_json_schema()}",
            },
            {
                "role": "user",
                "content": build_code_answer_prompt(question),
            },
        ],
        "temperature": 0.0,
        "max_tokens": 8192,
        "top_p": random.uniform(0.9, 1.0),
        "seed": random.randint(0, 1e9),  # needed for OpenAI
    }
    try:
        completion = await client.chat.completions.create(**kwargs)
        # print(f"Generated completion: {completion}")
        return model, completion
    except Exception as e:
        print(f"Error occurred while generating code answer: {e}")
        pass

    return model, None


def build_code_answer_prompt(question) -> str:
    CODE_ANS_PROMPT = """
    System:
    - You must assume that you do not have access to the file system, therefore if any test data is provided, you must store it in memory appropriately in the necessary variable and not in a file.
    - You must not provide any other text or explanations.
    - You must provide all code required to ensure that your solution is complete.
    - Do not leave out any details for brevity.
    - Additionally, ensure that your code solution directly executes any functions required to provide the solution to the task.
    - Your solution must not involve the useage of a terminal. If you require any inputs from the user, you must provide the functionality of the user input in your code.
    - You are able to write to multiple output file formats depending on your specific use case
    - Remember to include installation commands for any dependencies required for the code to run
    - Ensure all output code is properly formatted with consistent quotation marks and special characters are correctly escaped to prevent syntax errors.
    - The provided code solution should be directly executable without requiring modifications to run successfully.

    Few-shot Example Outputs:
    {few_shot_examples}
    
    Question:
    {question}

    Answer according to the JSON_SCHEMA:
    """

    return textwrap.dedent(
        CODE_ANS_PROMPT.format(
            question=question,
            few_shot_examples=few_shot_example_outputs(),
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


async def build_prompt_responses_pair():
    import commons.dataset as dataset

    client = get_openai_client(Provider.OPENROUTER)
    # use these models because we can specify seed
    MAX_RETRIES = 3
    prompt = None
    for _ in range(MAX_RETRIES):
        model_choice = random.choice(dataset.GENERATOR_MODELS)
        prompt = await generate_question(client, model_choice)
        if prompt:
            break

    if not prompt:
        return None

    # NOTE @dev LLMs here were selected to be able to compare against the EvalPLus leaderboard
    # randomly sampled from pool of models
    answer_models = dataset.ANSWER_MODELS
    num_answer_models = int(os.getenv("NUM_ANSWER_MODELS", 4))
    selected_models = random.sample(
        answer_models, min(num_answer_models, len(answer_models))
    )

    results = await asyncio.gather(
        *[generate_answer(client, ans_model, prompt) for ans_model in selected_models]
    )

    responses = []
    for model, result in results:
        if not result:
            continue
        # result = parse_code_response(result)
        formatted_files = [
            {
                "filename": file.filename,
                "content": file.content,
                "language": file.language,
            }
            for file in result.files
        ]
        responses.append(
            {
                "model": model,
                "completion": {
                    "files": formatted_files,
                    "installation_commands": result.installation_commands,
                    "additional_notes": result.additional_notes,
                },
            }
        )
    return {"prompt": prompt, "responses": responses}


async def main():
    res = await build_prompt_responses_pair()
    print(f"{res=}")


if __name__ == "__main__":
    asyncio.run(main())