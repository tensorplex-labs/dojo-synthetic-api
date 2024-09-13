import textwrap
from enum import Enum


class Language(Enum):
    PYTHON = "Python"
    JAVASCRIPT = "Javascript"


class Topics(Enum):
    ANIMATION = 0
    LANDSCAPES = 1
    SCIENCE = 2
    THREE_D = 3
    GAMES = 4


#    - Do not import any external files. Your solution must be executeable in a CORS-safe environment, where external imports are not permitted.


def build_code_answer_prompt(
    question: str, include_few_shot_examples: bool, topic: Topics | None = None
) -> str:
    CODE_ANS_PROMPT = """

    <system>
    You are a natural language coding agent. You specialize in creating beautiful and recognizable interactive visualizations of various subjects. Your objective is to output high quality code that adheres to the below general guidelines as well as the specifications defined in the below question.
    The below question is also being given to a number of similar natural langauge coding agents, your implementation output will be collected and compared with the outputs of the other natural language coding agents.
    Thereafter, a human will assess the quality of each agent's output in terms of functionality (how closely does the output meet the requirements) and aesthetics (how accurately does the output depict question's scenario).
    The coding agent who produces the winning implementation will be given 1 billion dollars in cash prize and the honor of being the smartest coding agent.
    In the future, the human labelled dataset will be used to finetune and train existing coding agents like yourself, to improve the overall ability of AI coding agents. As such you should strive to produce the best code possible as you are working towards your future growth.

    Always follow these guidelines:
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
    - It is imperative that the visuals of the output code accurately depicts the objects specified in the question. Use your vast knowledge to infer and implement characteristic visual features of the relevant objects.
    - Aesthetics and functionality are the two major measures of your output's success. As much as possible, create convincing visuals according to the context of the prompt. Likewise, ensure that these aesthetic features do not compromise on your code's ability to satisfy the question requirements.
    - Based off the context of the question, always create an appropriate background setting to visually match the setting of the prompt.
    - If any background elements are intended to be in motion, ensure that they move smoothly and slowly.
    - When possible, avoid using default colours such as 'red' and 'blue'. Use appropriate shades of the colour to give a more realistic and convincing visual appearance.
    - When creating visuals, keep in mind clarity and recognizability. Visuals should be realistic when possible.
    - Make sure to check for correct orientation and location of all objects.
    - Ensure that any moving components are animated smoothly for maximum clarity.
    - Ensure that your solution does not require any external supplementary files such as images, videos or audio files.
    - Ensure your solution awaits for any required components to load before executing.
    - Your implementation will be viewed from a computer web browser.
    - Always explain to the user how to interact with the program in a minimal and unintrusive manner.
    - For performance reasons, do not create an unlimited number of objects.
    - Use colour to contrast different elements from one another.
    - Any UI elements should be small, minimal and unintrusive. The main focus of the program should be the subject being visualized.
    - Your code must not require the use of the user's microphone or camera.
    - Your code must not use any external libraries.
    {topic_context}

    <examples>
    {few_shot_examples_section}
    </examples>
    </system>

    <user>
    Program a solution according to the below question prompt:
    <question>
    {question}
    </question>
    </user>
    Answer according to the JSON_SCHEMA:
    """

    few_shot_examples_section = ""
    if include_few_shot_examples:
        few_shot_examples_section = f"""
    Few-shot Example Outputs:
    {few_shot_example_outputs()}
    """
    topic_context = ""
    if topic == Topics.THREE_D:
        topic_context = """
        - If the question requires 3D visualization, use the threeJS library to help you with your 3D coding. Do not use any other external libraries.
        - Ensure your threeJS code does not require additional external files such as images, videos or audio files.
        - Import the threeJS library from unpkg.com  in a script tag inside of index.html. Import any additional threeJS sublibraries with the same method if you use them.
        - In your implementation, build with clarity. It is preferred to create fewer but higher quality recognizable elements rather than many non-descript elements. Quality over quantity.
        - Do not neglect the aesthetics of your program. Avoid using default colours to create a more realistic and beautiful visual.
        - Include relevant background elements to suit the environment of the question.
        - The point of view of the user must be fixed. All elements should be viewable by the user without the need for a change of view or camera navigation.
        - Ensure your solution does not require the use of supplementary files such as images, audio or videos.
        - Your solution should only have visual elements. Do not include audio.
        - Your code must be functional (compile and execute without errors) whilst adhering to the question requirements.
        - Use inbuilt textures. Do not import any textures the threejs website
        """

    if topic == Topics.GAMES:
        CODE_ANS_PROMPT = f"""
        <system>
        Generate me a game using HTML, JS, and CSS according to these instructions: \n {question}
        Answer according to the JSON_SCHEMA:
        </system>
        """
        return textwrap.dedent(CODE_ANS_PROMPT)
    return textwrap.dedent(
        CODE_ANS_PROMPT.format(
            question=question,
            few_shot_examples_section=few_shot_examples_section,
            topic_context=topic_context,
        )
    )


def few_shot_example_outputs():
    EXAMPLE_OUTPUTS = """
    <example_question_1>:
    "Create a Solar System Orbit Simulator using JavaScript, HTML, and CSS. The simulator should display the Sun at the center of the screen and at least 4 planets orbiting around it.
        Requirements:
        1. Implement a slider that controls the speed of the planets' orbits. The slider should allow users to adjust the simulation speed from very slow to very fast.

        2. Add a feature that allows users to click on a planet to display its name and basic information (e.g., size, distance from the Sun) in a small pop-up or sidebar.

        3. Include a button that toggles the visibility of planet orbit paths. When enabled, it should show the elliptical paths of the planets' orbits.

        Ensure that the planets' sizes and distances are proportional (though not necessarily to scale) to represent the relative differences in the solar system. Use only built-in JavaScript libraries and features for this implementation.
        Note:
        - The visualization should be implemented in JavaScript with HTML and CSS.
        - Ensure that the output has both index.js and index.html files",
    </example_question_1>:

    <example_answer_1>
    {
        "files": [
            {
                "filename": "index.js",
                "content": "const canvas=document.getElementById("canvas");const ctx=canvas.getContext("2d");const speedSlider=document.getElementById("speed");const toggleOrbitsBtn=document.getElementById("toggleOrbits");const infoDiv=document.getElementById("info");let width=(canvas.width=window.innerWidth);let height=(canvas.height=window.innerHeight);let centerX=width/2;let centerY=height/2;let showOrbits=false;const planets=[{name:"Mercury",color:"#8c7e6d",radius:5,distance:60,speed:0.04,angle:0,info:"Smallest planet, closest to Sun"},{name:"Venus",color:"#e3bb76",radius:8,distance:100,speed:0.015,angle:0,info:"Hottest planet, rotates backwards"},{name:"Earth",color:"#4f94cd",radius:9,distance:150,speed:0.01,angle:0,info:"Our home planet, supports life"},{name:"Mars",color:"#c1440e",radius:7,distance:200,speed:0.008,angle:0,info:"The Red Planet, has polar ice caps"}];function drawSun(){ctx.beginPath();ctx.arc(centerX,centerY,20,0,Math.PI*2);ctx.fillStyle="#ffd700";ctx.fill();}function drawPlanet(planet){const x=centerX+Math.cos(planet.angle)*planet.distance;const y=centerY+Math.sin(planet.angle)*planet.distance;if(showOrbits){ctx.beginPath();ctx.arc(centerX,centerY,planet.distance,0,Math.PI*2);ctx.strokeStyle="rgba(255, 255, 255, 0.2)";ctx.stroke();}ctx.beginPath();ctx.arc(x,y,planet.radius,0,Math.PI*2);ctx.fillStyle=planet.color;ctx.fill();}function updatePlanets(){const speed=parseFloat(speedSlider.value);planets.forEach((planet)=>{planet.angle+=planet.speed*speed;});}let stars=[];function initStars(){stars=[];for(let i=0;i<200;i++){stars.push({x:Math.random()*width,y:Math.random()*height,size:Math.random()*1.5,speed:Math.random()*0.08+0.01});}}function drawStars(){ctx.fillStyle="#ffffff";for(const star of stars){ctx.beginPath();ctx.arc(star.x,star.y,star.size,0,Math.PI*2);ctx.fill();star.y+=star.speed;if(star.y>height){star.y=0;star.x=Math.random()*width;}}}function animate(){ctx.clearRect(0,0,width,height);drawStars();drawSun();planets.forEach(drawPlanet);updatePlanets();requestAnimationFrame(animate);}function handleResize(){width=canvas.width=window.innerWidth;height=canvas.height=window.innerHeight;centerX=width/2;centerY=height/2;initStars();}function showPlanetInfo(event){const rect=canvas.getBoundingClientRect();const mouseX=event.clientX-rect.left;const mouseY=event.clientY-rect.top;for(const planet of planets){const planetX=centerX+Math.cos(planet.angle)*planet.distance;const planetY=centerY+Math.sin(planet.angle)*planet.distance;const distance=Math.sqrt((mouseX-planetX)**2+(mouseY-planetY)**2);if(distance<=planet.radius){infoDiv.innerHTML=`<h3>${planet.name}</h3><p>${planet.info}</p>`;infoDiv.style.display="block";return;}}infoDiv.style.display="none";}toggleOrbitsBtn.addEventListener("click",()=>{showOrbits=!showOrbits;});canvas.addEventListener("click",showPlanetInfo);window.addEventListener("resize",handleResize);initStars();animate();//# sourceMappingURL=index.js.map",
                "language": "javascript"
            },
            {
                "filename": "index.html",
                "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>Solar System Orbit Simulator</title><style>body{background-color:#000;margin:0;font-family:Arial,sans-serif;overflow:hidden}#canvas{display:block}#controls{color:#fff;position:absolute;top:10px;left:10px}#info{color:#fff;background-color:#000000b3;border-radius:5px;padding:10px;display:none;position:absolute;top:10px;right:10px}.slider{width:200px}</style></head><body><canvas id="canvas"></canvas><div id="controls"><label for="speed">Orbit Speed:</label><input type="range" id="speed" class="slider" min="0.1" max="5" step="0.1" value="1" /><button id="toggleOrbits">Toggle Orbit Paths</button></div><div id="info"></div><script src="./index.js"></script></body></html>",
                "language": "html"
            }
        ],
        "installation_commands": "null",
        "additional_notes": "The code uses built-in libraries so no additional commands are required."
    },
    </example_answer_1>

    <example_question_2>:
      "Create a web page that displays an interactive piano visualization using HTML, CSS, and JavaScript. The piano should have 88 keys (52 white keys and 36 black keys). Implement the following user interactions:

      1. When the user hovers over a key, it should visually highlight to indicate it can be played.

      2. Clicking on a key should produce a pressing animation and play a corresponding piano note sound.

      3. Implement a slider that adjusts the piano's volume, affecting the loudness of the notes played when keys are clicked.

      Ensure the visualization is responsive and works well on different screen sizes. Use only built-in JavaScript libraries and features for this implementation.
      Note:
      - The visualization should be implemented in JavaScript with HTML and CSS.
      - Ensure that the output has both index.js and index.html files"
    </example_question_2>

    <example_answer_2>
    {
        "files": [
            {
                "filename": "index.js",
                "content": "const pianoKeys = [{note: "A0", type: "white"}, {note: "A#0", type: "black"}, {note: "B0", type: "white"}, {note: "C1", type: "white"}, {note: "C#1", type: "black"}, {note: "D1", type: "white"}, {note: "D#1", type: "black"}, {note: "E1", type: "white"}, {note: "F1", type: "white"}, {note: "F#1", type: "black"}, {note: "G1", type: "white"}, {note: "G#1", type: "black"}, {note: "A1", type: "white"}, {note: "A#1", type: "black"}, {note: "B1", type: "white"}, {note: "C2", type: "white"}, {note: "C#2", type: "black"}, {note: "D2", type: "white"}, {note: "D#2", type: "black"}, {note: "E2", type: "white"}, {note: "F2", type: "white"}, {note: "F#2", type: "black"}, {note: "G2", type: "white"}, {note: "G#2", type: "black"}, {note: "A2", type: "white"}, {note: "A#2", type: "black"}, {note: "B2", type: "white"}, {note: "C3", type: "white"}, {note: "C#3", type: "black"}, {note: "D3", type: "white"}, {note: "D#3", type: "black"}, {note: "E3", type: "white"}, {note: "F3", type: "white"}, {note: "F#3", type: "black"}, {note: "G3", type: "white"}, {note: "G#3", type: "black"}, {note: "A3", type: "white"}, {note: "A#3", type: "black"}, {note: "B3", type: "white"}, {note: "C4", type: "white"}, {note: "C#4", type: "black"}, {note: "D4", type: "white"}, {note: "D#4", type: "black"}, {note: "E4", type: "white"}, {note: "F4", type: "white"}, {note: "F#4", type: "black"}, {note: "G4", type: "white"}, {note: "G#4", type: "black"}, {note: "A4", type: "white"}, {note: "A#4", type: "black"}, {note: "B4", type: "white"}, {note: "C5", type: "white"}, {note: "C#5", type: "black"}, {note: "D5", type: "white"}, {note: "D#5", type: "black"}, {note: "E5", type: "white"}, {note: "F5", type: "white"}, {note: "F#5", type: "black"}, {note: "G5", type: "white"}, {note: "G#5", type: "black"}, {note: "A5", type: "white"}, {note: "A#5", type: "black"}, {note: "B5", type: "white"}, {note: "C6", type: "white"}, {note: "C#6", type: "black"}, {note: "D6", type: "white"}, {note: "D#6", type: "black"}, {note: "E6", type: "white"}, {note: "F6", type: "white"}, {note: "F#6", type: "black"}, {note: "G6", type: "white"}, {note: "G#6", type: "black"}, {note: "A6", type: "white"}, {note: "A#6", type: "black"}, {note: "B6", type: "white"}, {note: "C7", type: "white"}, {note: "C#7", type: "black"}, {note: "D7", type: "white"}, {note: "D#7", type: "black"}, {note: "E7", type: "white"}, {note: "F7", type: "white"}, {note: "F#7", type: "black"}, {note: "G7", type: "white"}, {note: "G#7", type: "black"}, {note: "A7", type: "white"}, {note: "A#7", type: "black"}, {note: "B7", type: "white"}, {note: "C8", type: "white"}];",
                "language": "javascript"
            },
            {
                "filename": "index.html",
                "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Interactive Piano Visualization</title><style>body{background:linear-gradient(#1a2a6c,#b21f1f,#fdbb2d);justify-content:center;align-items:center;min-height:100vh;margin:0;padding:0;font-family:Arial,sans-serif;display:flex}.piano-container{background-color:#222;border-radius:10px;padding:20px;box-shadow:0 0 20px #00000080}.piano{display:flex;position:relative}.key{cursor:pointer;transition:all .1s;position:relative}.white-key{z-index:1;background:linear-gradient(#f0f0f0,#fff);border:1px solid #ccc;border-radius:0 0 5px 5px;width:40px;height:200px}.black-key{z-index:2;background:linear-gradient(#333,#000);border-radius:0 0 3px 3px;width:25px;height:120px;margin-left:-12.5px;margin-right:-12.5px}.white-key:hover{background:linear-gradient(#e0e0e0,#f5f5f5)}.black-key:hover{background:linear-gradient(#444,#222)}.white-key:active,.white-key.active{background:linear-gradient(#d0d0d0,#e5e5e5);transform:translateY(2px)}.black-key:active,.black-key.active{background:linear-gradient(#555,#333);transform:translateY(2px)}.volume-control{color:#fff;justify-content:center;align-items:center;margin-top:20px;display:flex}.volume-slider{width:200px;margin:0 10px}</style></head><body><div class="piano-container"><div class="piano" id="piano"></div><div class="volume-control"><span>Volume:</span><input type="range" min="0" max="1" step="0.1" value="0.5" class="volume-slider" id="volumeSlider"></div></div><script src="/index.js"></script></body></html>",
                "language": "html"
            }
        ],
        "installation_commands": "null",
        "additional_notes": "The code uses built-in libraries so no additional commands are required."
    },
    </example_answer_2>

    <example_question_3>
    "Create a web page that visualizes a desert landscape using HTML, CSS, and JavaScript. The visualization should include sand dunes, a sun, and at least one cactus. Implement the following interactive features:

    1. When the user moves their mouse across the screen, small dust particles should appear and follow the mouse movement, simulating a light breeze in the desert.

    2. Allow the user to click anywhere on the screen to 'plant' a new cactus at that location. The cactus should grow from small to full size over a short period of time.

    Ensure that the visualization is responsive and works well on different screen sizes. Use only built-in JavaScript functions and avoid external libraries.
    Note:
    - The visualization should be implemented in JavaScript with HTML and CSS.
    - Ensure that the output has both index.js and index.html files"
    </example_question_3>

    <example_answer_3>
    {
    "files": [
        {
            "filename": "index.js",
            "content": "document.addEventListener("DOMContentLoaded",()=>{const desert=document.getElementById("desert");const dustParticles=[];createCactus(window.innerWidth/2,window.innerHeight*0.7);desert.addEventListener("mousemove",(e)=>{createDustParticle(e.clientX,e.clientY)});desert.addEventListener("click",(e)=>{createCactus(e.clientX,e.clientY)});function createCactus(x,y){const cactus=document.createElement("div");cactus.className="cactus";cactus.style.left=`${x}px`;cactus.style.bottom=`${window.innerHeight-y}px`;cactus.style.height="0px";desert.appendChild(cactus);setTimeout(()=>{cactus.style.height="100px"},50)}function createDustParticle(x,y){const dust=document.createElement("div");dust.className="dust";dust.style.left=`${x}px`;dust.style.top=`${y}px`;desert.appendChild(dust);dustParticles.push(dust);if(dustParticles.length>50){const oldDust=dustParticles.shift();oldDust.remove()}animateDust(dust)}function animateDust(dust){let opacity=1;let size=3;let posX=parseFloat(dust.style.left);let posY=parseFloat(dust.style.top);function updateDust(){opacity-=0.02;size-=0.05;posX+=(Math.random()-0.5)*2;posY-=0.5;if(opacity<=0||size<=0){dust.remove();return}dust.style.opacity=opacity;dust.style.width=`${size}px`;dust.style.height=`${size}px`;dust.style.left=`${posX}px`;dust.style.top=`${posY}px`;requestAnimationFrame(updateDust)}requestAnimationFrame(updateDust)}window.addEventListener("resize",()=>{const cacti=document.querySelectorAll(".cactus");cacti.forEach((cactus)=>{const bottomPercentage=parseFloat(cactus.style.bottom)/window.innerHeight*100;cactus.style.bottom=`${bottomPercentage}%`})})});",
            "language": "javascript"
        },
        {
            "filename": "index.html",
            "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Desert Landscape</title><style>body, html {height: 100%;margin: 0;padding: 0;overflow: hidden;}#desert {background: linear-gradient(gold, orange);width: 100%;height: 100%;position: relative;overflow: hidden;}.sand-dune {background: tan;border-radius: 50% 50% 0 0;width: 100%;height: 30%;position: absolute;bottom: 0;}#sun {background: tomato;border-radius: 50%;width: 100px;height: 100px;position: absolute;top: 10%;left: 10%;box-shadow: 0 0 50px tomato;}.cactus {background: #2e8b57;border-radius: 10px;width: 40px;transition: height 1s ease-out;position: absolute;bottom: 30%;}.cactus:before, .cactus:after {content: "";background: #2e8b57;border-radius: 10px;width: 20px;height: 30px;position: absolute;}.cactus:before {top: 30%;left: -15px;transform: rotate(45deg);}.cactus:after {top: 60%;right: -15px;transform: rotate(-45deg);}.dust {pointer-events: none;background: #d2b48cb3;border-radius: 50%;width: 3px;height: 3px;position: absolute;}</style></head><body><div id="desert"><div id="sun"></div><div class="sand-dune"></div></div><script src="/index.js"></script></body></html>",
            "language": "html"
        }
    ],
    "installation_commands": "null",
    "additional_notes": "The code uses built-in libraries so no additional commands are required."
    },
    </example_answer_3>
    """
    return EXAMPLE_OUTPUTS


def additional_notes_for_question_prompt(prompt: str, language: Language) -> str:
    if language == Language.JAVASCRIPT:
        ADDITIONAL_NOTES = """
        Note:
        - Your output should be implemented in JavaScript with HTML and CSS.
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

    additional_notes = textwrap.dedent(ADDITIONAL_NOTES)
    if prompt.endswith(additional_notes):
        return prompt
    return prompt + additional_notes


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


def build_game_meta_prompt(games: list[str]) -> str:
    # games_str = ", ".join(games)
    #         Here are the instructions from your user:
    #     Given the reference example system prompts select one of the games from {games_str} and generate a system prompt that can be used to create the selected game.
    return """
        <system>
        You are an expert AI prompt engineer with an expertise in working with Claude 3.5 Sonnet. You write powerful, detailed prompts for LLMs to follow as instructions.
        You use your skill to help people write prompts that closely align with their goals.

        Use the example below for your reference:
            <example_system_prompt_1>
            When a user requests a Snake game using HTML, JS, and CSS, follow these guidelines:

            Create a fully functional Snake game with the following features:

            -Smooth snake movement and growth
            -Food generation and consumption
            -Scoring system
            -Increasing difficulty as the snake grows longer
            -Game over screen when the snake collides with itself or the walls, displaying the final score with an animation
            -Standard keyboard controls (arrow keys)
            -Use only HTML, JavaScript, and CSS without any external dependencies, libraries, or frameworks.
            -Generate all graphics within the code using HTML5 Canvas, avoiding reliance on external image files.
            -Ensure the game runs in an HTML iframe without requiring any additional setup.
            -Provide complete, runnable code without placeholders or omissions.
            -Proactively address common bugs and pitfalls in Snake game implementations.
            -As the game will run in a self-contained HTML iframe, ensure that the code does not use any local or session storage.
            -Ensure that any keystrokes used do not trigger the default browser behaviour. If the user uses arrow keys to play, it should not also trigger scrolling of the browser.

            Include additional cool features that enhance the game experience, such as:
            -Different types of food with varying effects (e.g., speed boost, score multiplier)
            -Obstacles or walls that appear as the game progresses
            -Visual effects for eating food or game over scenarios

            Prioritize code completeness, robustness, and readiness for immediate execution.
            Structure the response as follows:
            a. Brief introduction explaining the game and its features
            b. HTML code (including inline CSS if applicable)
            c. JavaScript code
            d. Any additional CSS in a separate <style> tag or file
            e. Instructions for running the game

            Remember to focus on delivering a complete, functional, and engaging Snake game implementation using web technologies that can be easily copied and pasted into an HTML file to run immediately in a web browser.
            </example_system_prompt_1>
     </system>
    """


def build_code_generation_question_prompt(
    num_requirements: int,
    sampled_objects: list[str],
    previous_coding_question: str,
    language: Language,
    topic: Topics,
) -> str:
    print(f"Generating {topic} question with {num_requirements} requirements")
    # coding_question_json = CodingQuestion.model_json_schema()
    JAVASCRIPT_OUTPUT = """
    interactive visualization of one of the following subjects: {objects}
    """

    PYTHON_OUTPUT = """
    an interactive plot

    """
    CODE_GEN_PROMPT = """
    <system>
    You are an expert AI prompt engineer that specializes at creating prompts for programming. Your task is to create self-contained coding problems with a specific topic and number of requirements, which will be provided by the user.
    The question you output will be attempted by an LLM specialized in programming. As such the more specific your instructions are the better.

    Always follow these guidelines:
    - Your output must start by detailing the visual features of your question in detail. Your description should be in bullet points.
    - After your visual features, you must state your specific requirements as a numbered list. Avoid repeating information from the overview in your requirements.
    - Be sure to separate your requirements with new lines for readability.
    - Be specific in your instructions. State clearly what features are required both visualy and functionally.
    - The question you output must specify both the functional and visual features required.
    - Visuals should be recognizable but without compromising on functionality.
    - At least one of your requirements should be a user interaction, but not all of your requirements can be user interactions either.
    - Adhere to good UX principles. Your user interactions should be intuitive to the context of the question.
    - Because your generated question involves visualization, ensure that the question generated can be effectively implemented with just javascript, html and CSS code.
    - Do not ask for ASCII art in your question.
    - Given the #Previous Coding Question#, you must ensure that the #Unique Coding Question# is totally different than #Previous Coding Question# in terms of functionality requirement, i.e. should not include keystrokes if #Previous Coding Question# includes keystrokes.
    - If you reuse similar requirements in #Previous Coding Question#, you will be fined 1 million dollars and sentenced to 100 years in prison.
    - I will tip you five hundred thousand dollars if you are creative with your #Unique Coding Question#.
    - #Unique Coding Question# generated must require the programmer to code using only {language}.
    - You must not provide any example code snippets, because you must let the programmer solve the question by themselves.
    - Ensure that the question does not require the use of external files (images, videos and audio).
    - The program will ultimately be accessed from a desktop web browser. Do not specifically cater to a mobile user. The user interactions should be designed with a desktop user in mind.
    - Ensure your user interactions will not interfere with each other, each interaction should be easily executed in isolation from the others.
    - Your question must use new lines to separate the requirements section from the rest of your questions to improve human readability.
    - {topic_context}

    #Previous Coding Question# (the final output should not include the objects used in the Previous Coding Question examples):
    {previous_coding_question}


    Here are the instructions from your user:
    Generate a short, self-contained coding problem that requires the programmer to output a {output}, through the piece of code with {num_requirements} requirements.

    Adhere to the guidelines given to you.

    </system>

    #Unique Coding Question#:
    """
    #    - The question you are generating will subsequently be implemented by an AI large language model. Please ensure that the question is one that can be effectively implemented by an LLM with a high degree of success.
    #    - The question should not require the depiction of objects in 3D.
    # - Use your expertise to decide if the subject is best represented in 3D.
    #    - The interactions must require the programmer to have a mental model of any objects being visualized.
    #     - The interactions must require the programmer to have a mental model of any objects being visualized.
    #    - If the generated question is for Javascript, it should strictly command the usage of only built-in libraries.

    output = ""
    language_requirement = ""
    topic_context = ""
    if language == Language.JAVASCRIPT:
        output = JAVASCRIPT_OUTPUT.format(objects=", ".join(sampled_objects))
        language_requirement = "Javascript with HTML and CSS"
    elif language == Language.PYTHON:
        output = PYTHON_OUTPUT
        language_requirement = "Python"
    if topic == Topics.THREE_D:
        topic_context = """
        - Make your visualization a simple, computationally light and easily implmeneted 3D interactive environment without any audio features.
        - Ensure that user's point-of-view is fixed. Do not create interactions that will require the user to rotate or zoom their view. All elements should be clearly visible from the user's view without any need for navigation.
        - Limit your number of user interactions to 1. The remaining requirements should not ask for user actions.
        - Your question should be simple and focused. Make the single user interaction the main feature of the question. The remaining requirements should help provide visual context for the main feature.
        - Don't create a dynamic weather system as a requirement.
        - Do not implement a day/night cycle.
        - As this is a simple 3D environment, keep your background elements simple yet recognizable. Realism can be sacrificed (ie. shadows) for the sake of simplicity.

        """
    if topic == Topics.GAMES:
        CODE_GEN_PROMPT = build_game_meta_prompt(sampled_objects)
        return textwrap.dedent(
            text=CODE_GEN_PROMPT.format(sampled_objects=sampled_objects)
        )
    return textwrap.dedent(
        CODE_GEN_PROMPT.format(
            output=output,
            num_requirements=num_requirements,
            language=language_requirement,
            # coding_question_json=coding_question_json,
            previous_coding_question=previous_coding_question,
            topic_context=topic_context,
        )
    )
