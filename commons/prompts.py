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

PROMPT = """



"""
