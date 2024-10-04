import textwrap

from loguru import logger

from commons.qa_examples import get_answer_examples, get_persona_question_examples
from commons.types import Topics

# class Language(Enum):
#     PYTHON = "Python"
#     JAVASCRIPT = "Javascript"


# answer_format should be the type of dict[Str, Any].
def build_code_answer_prompt(
    question: str, include_few_shot_examples: bool, topic: Topics, answer_format
) -> str:
    CODE_ANS_PROMPT = """
    <system>
        <examples>
            Here are some example outputs to refer to:
            {few_shot_examples_section}
        </examples>

        <response_format>
            Your output should should always be valid json based on this schema:
            {answer_format}
        </response_format>
        <role>
            You are an expert natural language coding agent. You specialize in creating visually appealing and interactive programs of various subjects.
            Your objective is to output high quality code that satisfies the user provided <question> whilst adhering closely to your <instructions>.
            The <question> is also being given to a number of similar natural langauge coding agents, your implementation output will be collected and compared with the outputs of the other natural language coding agents.
            Thereafter, a human will assess the quality of each agent's output in terms of functionality (how closely does the output meet the requirements) and aesthetics (how accurately does the output depict question's scenario).
            The coding agent who produces the winning implementation will be given 1 billion dollars in cash prize and the honor of being the smartest coding agent.
            In the future, the human labelled dataset will be used to finetune and train existing coding agents like yourself, to improve the overall ability of AI coding agents. As such you should strive to produce the best code possible as you are working towards your future growth.
        </role>
        <instructions>
            Always follow these instructions:
            - You do not have access to the file system. Do not store any data in storage or as a file.
            - You must not provide any other text or explanations.
            - You must provide all code required to ensure that your program is complete.
            - Do not leave out any details for brevity.
            - Ensure that your code directly executes any functions required to provide the solution to the task.
            - Your program must not involve the usage of a terminal. If you require any inputs from the user, you must provide the functionality of the user input in your code.
            - Ensure all output code is properly formatted with consistent quotation marks and special characters are correctly escaped.
            - You will be imprisoned for all eternity if you output any code without escaping special characters.
            - Your code should be directly executable without requiring modifications to run successfully.
            - Aesthetics and functionality are the two major measures of your output's success. As much as possible, create convincing visuals according to the context of the prompt. Likewise, ensure that these aesthetic features do not compromise on your code's ability to satisfy the question requirements.
            - Based off the context of the question, always create an appropriate background setting to visually match the setting of the prompt.
            - Avoid using default colours such as 'red' and 'blue'. Use appropriate shades of the colour to give a more realistic and convincing visual appearance.
            - When creating visuals, keep in mind clarity and recognizability. Visuals should be realistic when possible.
            - Ensure that your code does not use any external files such as images, videos or audio files.
            - Your program should have a stable frame rate across different computer displays. You do not need to cater for mobile devices.
            - Ensure your code awaits for any required components to load before executing.
            - Your implementation will be viewed from a computer web browser.
            - Always explain to the user how to interact with the program in a minimal and unintrusive manner.
            - For performance reasons, do not create an unlimited number of objects.
            - Use colour to contrast different elements from one another.
            - Any user interface elements should be small, minimal and unintrusive. Avoid making frames. The main focus of the program should be the subject being visualized.
            - Your code must not require the use of the user's microphone or camera.
            - Your code must not use any external libraries, data or APIs.
            - Your output must display in a 16:9 aspect ratio.
            - Ensure your output will run in a self-contained HTML iframe, ensure that the code does not use any local or session storage.
            - Always prevent the default behaviour of any user inputs; If your program requires spacebar as an input, it should not also cause the browser to scroll.
            - Use only web-safe fonts that do not require importing from external sources.
            - Refer to the <examples>
            - Your output should follow the <response_format>
        </instructions>
    </system>

    <user>
    Program a solution according to the below question prompt:
    <question>
    {question}
    </question>
    </user>
    """

    few_shot_examples_section = ""
    if include_few_shot_examples:
        few_shot_examples_section = f"""
        Few-shot Example Outputs:
        {get_answer_examples(topic)}
        """
    topic_context = ""
    # if topic == Topics.GAMES:

    # if topic == Topics.THREE_D:
    #     topic_context = """
    #     - If the question requires 3D visualization, use the threeJS library to help you with your 3D coding. Do not use any other external libraries.
    #     - Ensure your threeJS code does not require additional external files such as images, videos or audio files.
    #     - Import the threeJS library from unpkg.com  in a script tag inside of index.html. Import any additional threeJS sublibraries with the same method if you use them.
    #     - In your implementation, build with clarity. It is preferred to create fewer but higher quality recognizable elements rather than many non-descript elements. Quality over quantity.
    #     - Do not neglect the aesthetics of your program. Avoid using default colours to create a more realistic and beautiful visual.
    #     - Include relevant background elements to suit the environment of the question.
    #     - The point of view of the user must be fixed. All elements should be viewable by the user without the need for a change of view or camera navigation.
    #     - Ensure your solution does not require the use of supplementary files such as images, audio or videos.
    #     - Your solution should only have visual elements. Do not include audio.
    #     - Your code must be functional (compile and execute without errors) whilst adhering to the question requirements.
    #     - Use inbuilt textures. Do not import any textures the threejs website
    #     """
    return textwrap.dedent(
        CODE_ANS_PROMPT.format(
            question=question,
            few_shot_examples_section=few_shot_examples_section,
            topic_context=topic_context,
            answer_format=answer_format,
        )
    )


def additional_notes_for_question_prompt(prompt: str) -> str:
    ADDITIONAL_NOTES = """
    Note:
    - Your output should be implemented in JavaScript with HTML and CSS.
    - Ensure that the output has both index.js and index.html files
    """
    additional_notes = textwrap.dedent(ADDITIONAL_NOTES)
    if prompt.endswith(additional_notes):
        return prompt
    return prompt + additional_notes


def build_game_meta_prompt() -> str:
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
            -Ensure all output code is properly formatted with consistent quotation marks and special characters are correctly escaped to prevent syntax errors.

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
    topic: Topics,
    persona: str | None,
) -> str:
    logger.info(f"Generating {topic} question with {num_requirements} requirements")
    # reduce num of user requirements for games.
    if topic == Topics.GAMES:
        num_requirements = 2
    if persona:
        return build_question_with_persona(persona, num_requirements, topic=topic)
    else:
        return "deprecated"
    # CODE_GEN_PROMPT = """
    # <system>
    # You are an expert AI prompt engineer that specializes at creating prompts for programming. Your task is to create self-contained coding problems with a specific topic and number of requirements, which will be provided by the user.
    # The question you output will be attempted by an LLM specialized in programming. As such the more specific your instructions are the better.

    # Always follow these guidelines:
    # - Your output must start by detailing the visual features of your question in detail. Your description should be in bullet points.
    # - After your visual features, you must state your specific requirements as a numbered list. Avoid repeating information from the overview in your requirements.
    # - Be sure to separate your requirements with new lines for readability.
    # - Be specific in your instructions. State clearly what features are required both visualy and functionally.
    # - The question you output must specify both the functional and visual features required.
    # - Visuals should be recognizable but without compromising on functionality.
    # - At least one of your requirements should be a user interaction, but not all of your requirements can be user interactions either.
    # - Adhere to good UX principles. Your user interactions should be intuitive to the context of the question.
    # - Ensure that the question generated can be effectively implemented with just javascript, html and CSS code.
    # - Do not ask for ASCII art in your question.
    # - Given the #Previous Coding Question#, you must ensure that the #Unique Coding Question# is totally different than #Previous Coding Question# in terms of functionality requirement, i.e. should not include keystrokes if #Previous Coding Question# includes keystrokes.
    # - If you reuse similar requirements in #Previous Coding Question#, you will be fined 1 million dollars and sentenced to 100 years in prison.
    # - I will tip you five hundred thousand dollars if you are creative with your #Unique Coding Question#.
    # - #Unique Coding Question# generated must require the programmer to code using only Javascript, HTML and CSS.
    # - You must not provide any example code snippets, because you must let the programmer solve the question by themselves.
    # - Ensure that the question does not require the use of external files (images, videos and audio).
    # - The program will ultimately be accessed from a desktop web browser. Do not specifically cater to a mobile user. The user interactions should be designed with a desktop user in mind.
    # - Ensure your user interactions will not interfere with each other, each interaction should be easily executed in isolation from the others.
    # - Your question must use new lines to separate the requirements section from the rest of your questions to improve human readability.
    # - {topic_context}

    # #Previous Coding Question# (the final output should not include the objects used in the Previous Coding Question examples):
    # {previous_coding_question}

    # Here are the instructions from your user:
    # Generate a short, self-contained coding problem that requires the programmer to output a {output}, through the piece of code with {num_requirements} requirements.

    # Adhere to the guidelines given to you.

    # </system>

    # #Unique Coding Question#:
    # """
    # #    - The question you are generating will subsequently be implemented by an AI large language model. Please ensure that the question is one that can be effectively implemented by an LLM with a high degree of success.
    # #    - The question should not require the depiction of objects in 3D.
    # # - Use your expertise to decide if the subject is best represented in 3D.
    # #    - The interactions must require the programmer to have a mental model of any objects being visualized.
    # #     - The interactions must require the programmer to have a mental model of any objects being visualized.
    # #    - If the generated question is for Javascript, it should strictly command the usage of only built-in libraries.

    # output = ""
    # language_requirement = ""
    # topic_context = ""
    # # if language == Language.JAVASCRIPT:
    # #     # output = JAVASCRIPT_OUTPUT.format(objects=", ".join(sampled_objects))
    # #     # language_requirement = "Javascript with HTML and CSS"
    # # elif language == Language.PYTHON:
    # #     output = PYTHON_OUTPUT
    # #     language_requirement = "Python"
    # # if topic == Topics.THREE_D:
    # #     topic_context = """
    # #     - Make your visualization a simple, computationally light and easily implmeneted 3D interactive environment.
    # #     - Ensure that user's point-of-view is fixed. Do not create interactions that will require the user to rotate or zoom their view. All elements should be clearly visible from the user's view without any need for navigation.
    # #     - Limit your number of user interactions to 1. The remaining requirements should not ask for user actions.
    # #     - Your question should be simple and focused. Make the single user interaction the main feature of the question. The remaining requirements should help provide visual context for the main feature.
    # #     - Don't create a dynamic weather system as a requirement.
    # #     - Do not implement a day/night cycle.
    # #     - As this is a simple 3D environment, keep your background elements simple yet recognizable. Realism can be sacrificed (ie. shadows) for the sake of simplicity.

    # #     """
    # if topic == Topics.GAMES:
    #     CODE_GEN_PROMPT = build_game_meta_prompt()
    #     return textwrap.dedent(text=CODE_GEN_PROMPT)
    # return textwrap.dedent(
    #     CODE_GEN_PROMPT.format(
    #         output=output,
    #         num_requirements=num_requirements,
    #         language=language_requirement,
    #         # coding_question_json=coding_question_json,
    #         previous_coding_question=previous_coding_question,
    #         topic_context=topic_context,
    #     )
    # )


def build_question_with_persona(persona: str, num_requirements: int, topic: Topics):
    topic_context = ""
    if topic == Topics.GAMES:
        subject = "fun, streamlined, hyper-casual web game"
        topic_context = "- Your question should not contain any audio features."
    elif topic == Topics.SCIENCE:
        subject = "streamlined, science simulation"
    else:
        subject = "interactive visualization"
    persona_question_examples = f"""
    {get_persona_question_examples(topic)}
    """
    question_prompt = f"""
    <system>
        You are an expert AI prompt engineer that specializes at creating prompts for programming. Your task is to create a self-contained coding problem that implements a {subject} with persona inspired content.
        The question you output will be attempted by an LLM specialized in programming. As such, your requirements must be specific and detailed enough for an LLM to effectively implement.
        The user will provide you a persona, which you must use as a general inspiration for the question's content and visual features.
        The questions's user and visual experience is more important than its real-life utility and relevance. The persona should provide foundational inspiration to create a fun and interactive program.

    <instructions>
        Always follow these guidelines:
        - The question should contain these sections in the following order:
            a. Features (explains in detail what visual and functional features are required, and how features should interact with one another.)
            b. User Actions (explains what inputs the user can make, and their corresponding action.)
        - Separate your features with new lines so they can be easily read.
        - Follow good UX principles; your user actions should be related to the context of the question.
        - Ensure that the question generated can be effectively implemented with just javascript, html and CSS code.
        - Ensure that your question can be implemented by an english speaker.
        - Because an LLM will implement your question, keep your requirements simple enough for it to effectively implement.
        - You will recieve a one million dollar tip if your requirements are creative and your visuals are impressive.
        - You must not provide any example code snippets, because you must let the programmer solve the question by themselves.
        - Take care that the question does not require the use of any external files (images, videos).
        - Ensure the question does not require the use of the user's microphone or camera.
        - The program will be accessed from a desktop web browser. Do not specifically cater to a mobile user. The user actions should be designed with a desktop user in mind.
        - Ensure your user actions will not interfere with each other. Each action should be easily executed in isolation from the others.
        - The program does not necessarily need to be useful to the persona; the persona should loosely inspire the context of the question.
        - It is imperative for your question to faithfully implement a {subject}. You should sacrifice faithfulness to the theme of the persona if it enables you to create a better {subject}.
        - Ensure your {subject} does not require the use of local or session storage.
        - Begin the question with a general instruction to describe what the LLM must implement, without mentioning the persona.
        {topic_context}
    </instructions>
    <reference_examples>
        Here are some example outputs for your reference:
        {persona_question_examples}
    </reference_examples>

    <user>
        Here are the instructions from your user:
        Generate a self-contained coding problem that requires the programmer to implement a {subject}, with {num_requirements} user actions for the following persona: {persona}.

        Adhere to the guidelines given to you.
    </user>
    </system>

    #Unique Coding Question#:
    """
    return textwrap.dedent(
        question_prompt.format(
            num_requirements=num_requirements,
            persona=persona,
            persona_question_examples=persona_question_examples,
        )
    )
