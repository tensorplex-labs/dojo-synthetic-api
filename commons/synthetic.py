import asyncio
import json
import os
import random
import traceback
import uuid
from enum import Enum
from typing import Dict, List, Tuple, cast

import instructor
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langfuse.decorators import langfuse_context, observe
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tenacity import (
    AsyncRetrying,
    RetryError,
    stop_after_attempt,
)

from commons.code_executor.simple_cot import code_feedback_loop
from commons.config import ANSWER_MODELS, GENERATOR_MODELS
from commons.executor.python_executor import PythonExecutor
from commons.executor.utils import ExecutionError
from commons.llm.llm_api import (
    Provider,
    get_llm_api_client,
)
from commons.prompt_builders import (
    Language,
    Topics,
    additional_notes_for_question_prompt,
    build_code_answer_prompt,
    build_code_generation_question_prompt,
    build_game_meta_prompt,
    build_python_fix_prompt,
    build_python_review_prompt,
)

load_dotenv()


# define some types
LlmClient = AsyncOpenAI | instructor.AsyncInstructor


def log_llm_usage(completion):
    return {
        "input": completion.usage.prompt_tokens,
        "output": completion.usage.completion_tokens,
        "unit": "TOKENS",
    }


def log_retry_info(retry_state):
    """Meant to be used with tenacity's before_sleep callback"""
    logger.warning(
        f"Retry attempt {retry_state.attempt_number} failed with exception: {retry_state.outcome.exception()}",
    )
    logger.warning(f"Traceback: {traceback.format_exc()}")


class CodingQuestion(BaseModel):
    question: str = Field(
        description="Coding question to be solved by a software engineer"
    )


class FileObject(BaseModel):
    filename: str = Field(description="Name of the file")
    content: str = Field(description="The code contents of the file.")
    language: str = Field(description="Programming language of the file")


class CodeAnswer(BaseModel):
    files: List[FileObject] = Field(
        description="Array of FileObject, that are part of the code solution. Must include index.html, and index.js a Javascript solution"
    )
    installation_commands: str = Field(
        description="Terminal commands for the code to be able to run to install any third-party packages for the code to be able to run"
    )
    additional_notes: str | None = Field(
        description="Any additional notes or comments about the code solution"
    )


class ErrorAnswer(BaseModel):
    error: str = Field(description="The problem in the code solution")
    solution: str = Field(
        description="The solution to the problem in the code solution"
    )
    changes: str | None = Field(
        description="Any changes that can be made to the code solution to fit the requirements"
    )
    reasoning: str | None = Field(
        description="The reasoning behind the solution to the problem in the code solution"
    )


class AugmentationLevel(Enum):
    ORIGINAL = 0
    REMOVE_REQUIREMENTS = 1
    CHANGE_REQUIREMENTS = 2
    CHANGE_ANIMATION_OBJECT = 3


class ResponseStrategy(Enum):
    AUGMENTATION_DETERIORIATE = 0
    NO_AUGMENTATION = 1


async def parse_code_response(result_object: CodeAnswer) -> CodeAnswer:
    """Ensure that necessary files appended for python and javascript"""
    result_object = await append_codesandbox_files(result_object)
    # result_object = escape_double_quotes_in_files(result_object)
    return result_object


def handle_javascript_files(codeanswer_object: CodeAnswer) -> CodeAnswer:
    package_json_content = json.dumps(
        {
            "name": "javascript",
            "version": "1.0.0",
            "description": "The JavaScript template",
            "scripts": {
                "start": "parcel ./index.html",
                "build": "parcel build ./index.html",
            },
            "devDependencies": {
                "parcel": "^2.0.0",
                "babel-eslint": "^10.1.0",
                "eslint": "^7.2.0",
            },
            "keywords": ["css", "javascript"],
        },
        indent=4,
    )

    package_json_file = FileObject(
        filename="package.json",
        content=package_json_content,
        language="json",
    )
    codeanswer_object.files.append(package_json_file)
    return codeanswer_object


async def handle_python_files(codeanswer_object: CodeAnswer) -> CodeAnswer:
    print("in python")
    main_file: FileObject | None = None
    for file in codeanswer_object.files:
        if file.language.lower() == "python" and file.filename == "main.py":
            main_file = file
            break

    if not main_file:
        logger.info("No main.py file found in code answer of Python code")
        logger.info(codeanswer_object)
        raise Exception("No main.py file found in code answer of Python code")

    executor = PythonExecutor(code=main_file.content)
    try:
        loop = asyncio.get_event_loop()
        html = await loop.run_in_executor(None, executor.main)
    except ExecutionError as e:
        logger.error(f"Error occurred while executing Python code: {e}")
        raise e

    codeanswer_object.files = [
        FileObject(filename="index.html", content=html, language="html")
    ]

    return codeanswer_object


async def append_codesandbox_files(codeanswer_object: CodeAnswer) -> CodeAnswer:
    python_file_detected = any(
        file.language.lower() == "python" for file in codeanswer_object.files
    )
    if python_file_detected:
        codeanswer_object = await handle_python_files(codeanswer_object)

    # changed to always run this since handle_python_files returns html which needs the parcel stuff
    return handle_javascript_files(codeanswer_object)


@observe(as_type="generation", capture_input=False, capture_output=False)
async def _generate_objects_to_visualize(
    client: LlmClient, model: str, prev_used_objects: list[str], topic: Topics
):
    class PossibleObjects(BaseModel):
        objects: List[str] = Field(description="List of objects to visualize")

    blacklist = [
        "ferris wheel",
        "Bicycle",
        "Canyon",
        "fjord",
        "motorcycle",
        "bioluminescent",
        "sinkhole",
        "grand canyon",
        "carousel",
        "geode",
    ]

    logger.info(f"Generating {topic} objects to use for question with model: {model}")
    if topic == Topics.ANIMATION:
        prompt = f"""
        Give me a list of 30 tangible objects commonly used for animation coding questions, where the object can be interactively visualized in a basic web app that uses only javascript, HTML and CSS.

        Do not include the following: {', '.join(prev_used_objects+blacklist)}. Do not include any objects which are UI elements (such as loading spinners and progress bars.) Do not include any objects which are animals.

        Output the list as a valid JSON
        """
    elif topic == Topics.LANDSCAPES:
        prompt = f"""
        Give me a list of 30 recognizable natural phenomena that can be easily and simply visualized in 3D with a basic web app that uses only javascript, HTML and CSS.

        An LLM such as yourself will later have to generate the code for this program. So please ensure that the subject can feasibly be implemented by an LLM.

        Do not include the following {', '.join(prev_used_objects+blacklist)}.

        Output the list as a valid JSON
    """
    elif topic == Topics.SCIENCE:
        prompt = f"""
        Give me a list of 30 science experiments that can be demonstrated with a web app that uses only javascript, HTML and CSS.

        The experiments should be simple enough that a high school student could reasonably understand and have knowledge of it.

        An LLM such as yourself will later have to generate the code for this program. So please ensure that the subject can feasibly be implemented by an LLM.

        Do not include the following: {', '.join(prev_used_objects+blacklist)}.

        Please prioritize experiments which are interactive.

        Output the list as a valid JSON
    """
    elif topic == Topics.GAMES:
        prompt = f"""
        Give me a list of 30 popular video games that can be easily implemented with a web app that uses only javascript, HTML and CSS.

        The experiments should be simple enough that a high school student could reasonably understand and have knowledge of it.

        An LLM such as yourself will later have to generate the code for this program. So please ensure that the subject can feasibly be implemented by an LLM.

        Do not include the following: {', '.join(prev_used_objects+blacklist)}.

        Please prioritize experiments which are interactive.

        Output the list as a valid JSON
    """

    # logger.info(f"@@@ obj prompt: \n {prompt} \n ")
    kwargs = {
        "response_model": PossibleObjects,
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": prompt,
            }
        ],
        "temperature": random.uniform(0.7, 1.0),
        "max_tokens": 8192,  # 1024
        "top_p": random.uniform(0.9, 1.0),
    }
    if model.startswith("openai"):
        kwargs["seed"] = random.randint(0, cast(int, 1e9))  # needed for OpenAI
    response_model = await client.chat.completions.create(**kwargs)
    # logger.info(f"@@@ response_model: {response_model}")

    kwargs_clone = kwargs.copy()
    kwargs_clone["response_model"] = kwargs["response_model"].model_json_schema()
    langfuse_context.update_current_observation(
        input=kwargs_clone.pop("messages"),
        model=model,
        output=response_model.model_dump(),
        # usage=log_llm_usage(response_model.usage),
        metadata={
            "blacklist": blacklist,
            "prev_used_objects": prev_used_objects,
            "topic": topic,
            **kwargs_clone,
        },
    )
    logger.success(f"Got objects to visualize, completion={response_model=}")
    return response_model.objects


used_objects = []
previous_coding_question = ""
used_models = set()


@observe(as_type="generation", capture_input=False, capture_output=False)
async def generate_question(
    client: instructor.AsyncInstructor, model: str, language: Language, _topic: Topics
) -> tuple[str | None, Dict | None]:
    logger.info(f"Generating question with model: {model}")

    MAX_RETRIES = 5
    global used_objects
    global previous_coding_question
    global used_models

    # try generating until max_retries, then switch models
    try:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(MAX_RETRIES), before_sleep=log_retry_info
        ):
            with attempt:
                print(
                    f"Objects to be excluded in instruction generation: {used_objects}"
                )
                print(
                    f"Few shot instruction included in instruction generation: {previous_coding_question}"
                )
                # # randomly select one topic to be used to generate objects + question
                # selected_topic = random.choices(population=list(Topics), k=1)
                if language == Language.JAVASCRIPT:
                    print("Generating objects to visualize")
                    possible_objects = await _generate_objects_to_visualize(
                        client, model, used_objects, _topic
                    )
                    sampled_objects = random.sample(
                        possible_objects, random.randint(3, 5)
                    )
                    # logger.info(f"@@@ sampled objs: \n {sampled_objects} \n")
                    used_objects = sampled_objects

                kwargs = {
                    "response_model": CodingQuestion,
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": build_code_generation_question_prompt(
                                random.choices([3, 4], weights=[0.5, 0.5])[0],
                                used_objects,
                                previous_coding_question,
                                language,
                                topic=_topic,
                            ),
                        }
                    ],
                    "temperature": random.uniform(0.5, 0.75),
                    "max_tokens": 8192,
                    "top_p": random.uniform(0.9, 1.0),
                    "seed": random.randint(0, cast(int, 1e9)),  # needed for OpenAI
                }

                # need to meta-prompt first to generate the 'question prompt`
                if _topic == Topics.GAMES:
                    kwargs = {
                        "response_model": CodingQuestion,
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": build_game_meta_prompt(),
                            },
                            {
                                "role": "user",
                                "content": f"Select one of the games from {used_objects} and generate a system prompt that can be used to create the selected game.",
                            },
                        ],
                        "temperature": random.uniform(0.5, 0.75),
                        "max_tokens": 8192,
                        "top_p": random.uniform(0.9, 1.0),
                        "seed": random.randint(0, cast(int, 1e9)),  # needed for OpenAI
                    }

                logger.info(kwargs["messages"][0])
                response_model = await client.chat.completions.create(**kwargs)
                coding_question = response_model.question
                coding_question = additional_notes_for_question_prompt(
                    coding_question, language
                )

                kwargs_clone = kwargs.copy()
                kwargs_clone["response_model"] = kwargs[
                    "response_model"
                ].model_json_schema()
                langfuse_context.update_current_observation(
                    input=kwargs_clone.pop("messages"),
                    model=model,
                    output=response_model.model_dump(),
                    # usage=log_llm_usage(response_model.usage),
                    metadata={
                        "language": language,
                        "topic": _topic,
                        "used_objects": used_objects,
                        "used_models": used_models,
                        "previous_coding_question": previous_coding_question,
                        **kwargs_clone,
                    },
                )
                logger.success(f"Generated question: {coding_question}")
                previous_coding_question = coding_question
                return coding_question, kwargs
    except RetryError:
        logger.error(
            f"Failed to generate question after {MAX_RETRIES} attempts. Switching model."
        )
        used_models.add(model)
        remaining_models = [m for m in GENERATOR_MODELS if m not in used_models]
        # return if no models remaining
        if not remaining_models:
            logger.error("No generator models left to try.")
            return None, None
        new_model = random.choice(remaining_models)
        return await generate_question(client, new_model, language, _topic)
    except Exception as e:
        print(f"Error occurred while generating question: {e}")

    return None, None


@observe(as_type="generation", capture_input=False, capture_output=False)
async def generate_answer(
    client: LlmClient,
    model: str,
    question: str,
    language: Language,
    err: str | None = None,
    code: str | None = None,
    topic: Topics | None = None,
) -> Tuple[str, CodeAnswer | None]:
    """Generates a coding question answer for a given coding question."""
    import commons.config as config

    print(f"Generating code answer with model: {model}")
    if bool(err) != bool(code):
        raise ValueError("Both error and code must be provided or neither")

    messages = [
        {
            "role": "system",
            "content": f"You are an expert at outputting json. You always output valid json based on this schema: {CodeAnswer.model_json_schema()}",
        },
        {
            "role": "user",
            "content": build_code_answer_prompt(
                question, language.value == Language.JAVASCRIPT, topic=topic
            ),
        },
    ]

    if err and code:
        err_prompt = await generate_python_fix_prompt(
            client, model, code, err, question
        )
        messages.append({"role": "system", "content": err_prompt})
        logger.info(err_prompt)

    kwargs = {
        "response_model": CodeAnswer,
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 8192,
        "top_p": random.uniform(0.9, 1.0),
    }
    if model.startswith("openai"):
        kwargs["seed"] = random.randint(0, cast(int, 1e9))  # needed for OpenAI

    MAX_RETRIES = 2
    # logger.warning(f"@@@ ans gen {model} prompt: {kwargs['messages'][1]} \n")

    # try generating until max retries, then switch models
    try:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(MAX_RETRIES), before_sleep=log_retry_info
        ):
            with attempt:
                response_model = await client.chat.completions.create(**kwargs)

                kwargs_clone = kwargs.copy()
                kwargs_clone["response_model"] = kwargs[
                    "response_model"
                ].model_json_schema()
                langfuse_context.update_current_observation(
                    input=kwargs_clone.pop("messages"),
                    model=model,
                    output=response_model.model_dump(),
                    # usage=log_llm_usage(response_model.usage),
                    metadata={
                        "question": question,
                        "language": language,
                        "err": err,
                        "code": code,
                        "topic": topic,
                        **kwargs_clone,
                    },
                )
                # logger.warning(f"@@@ generate_answer(): {response_model} \n")
                return model, response_model
    except RetryError:
        logger.error(
            f"Failed to generate answer after {MAX_RETRIES} attempts. Switching model."
        )
        used_models.add(model)
        remaining_models = [m for m in config.ANSWER_MODELS if m not in used_models]
        # return if no models remaining
        if not remaining_models:
            logger.error("No answer models left to try.")
            return model, None
        new_model = random.choice(remaining_models)
        return await generate_answer(client, new_model, question, language)
    except Exception as e:
        print(f"Error occurred while generating code answer: {e}")

    return model, None


async def generate_python_fix_prompt(
    client: LlmClient,
    model: str,
    code: str,
    err: str,
    prompt: str,
) -> str:
    kwargs = {
        "response_model": ErrorAnswer,
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": f"You are an expert at outputting json. You always output valid json based on this schema: {ErrorAnswer.model_json_schema()}",
            },
            {
                "role": "user",
                "content": build_python_review_prompt(prompt, code, err),
            },
        ],
        "temperature": 0.0,
        "max_tokens": 8192,
        "top_p": random.uniform(0.9, 1.0),
    }
    if model.startswith("openai"):
        kwargs["seed"] = random.randint(0, cast(int, 1e9))  # needed for OpenAI
    try:
        completion = await client.chat.completions.create(**kwargs)
        # print(f"Generated completion: {completion}")
        logger.info(f"Generated error prompt: {completion}")
        return build_python_fix_prompt(
            code=code,
            err=completion.error,
            solution=completion.solution,
            changes=completion.changes,
        )
    except Exception as e:
        print(f"Error occurred while generating code answer: {e}")
        pass

    return build_python_fix_prompt(code=code, err=err)


async def generate_answer_with_feedback(
    client: LlmClient,
    model: str,
    question: str,
    language: Language,
    max_attempts: int = 3,
) -> Tuple[str, CodeAnswer | None]:
    previous_code = None
    err = None
    attempt_count = 0
    previous_err = None

    while attempt_count < max_attempts:
        model, result = await generate_answer(
            client, model, question, language, previous_code, err
        )
        if result is None:
            return model, None

        try:
            return model, await parse_code_response(result)
        except ExecutionError as e:
            err = e.err
            previous_code = e.code

            if err == previous_err:
                attempt_count += 1
            else:
                attempt_count = 0
                previous_err = err

    return model, None


def get_answer_model_ids(response_strategy: ResponseStrategy) -> str | list[str]:
    # NOTE @dev LLMs here were selected to be able to compare against the EvalPLus leaderboard
    # randomly sampled from pool of models
    if response_strategy == ResponseStrategy.NO_AUGMENTATION:
        num_answer_models = int(os.getenv("NUM_ANSWER_MODELS", 4))
        selected_models = random.sample(
            ANSWER_MODELS, min(num_answer_models, len(ANSWER_MODELS))
        )

        # check if enough answer models are specified
        if len(ANSWER_MODELS) < num_answer_models:
            logger.warning(
                f"Number of answer models is less than the specified number of models: {num_answer_models}"
            )
            raise RuntimeError("Error generating prompt-response pair")
        return selected_models

    elif response_strategy == ResponseStrategy.AUGMENTATION_DETERIORIATE:
        return random.choice(ANSWER_MODELS)


@observe(as_type="generation", capture_input=False, capture_output=False)
async def augment_question(
    client: LlmClient,
    model: str,
    question: str,
    augmentation_level: AugmentationLevel,
    topic: Topics,
) -> str:
    """Augment the question with the given model and augmentation level."""
    logger.info(
        f"Augmenting question with model and augmentation: {model}, {augmentation_level}"
    )
    augmentation_prompt = ""
    preamble = """
    <system>
    You are an LLM specializing in modifying existing coding questions to create similar yet distinct versions. Ultimately the new edited questions that you generate will be implemented by a programming agent. As such, use your vast knowledge of UX and software engineering principles to make intelligent yet distinguishable modifications.
    </system>
    """

    if augmentation_level == AugmentationLevel.REMOVE_REQUIREMENTS:
        augmentation_prompt = f"You must remove any 1 requirement from the following question: {question}. Ensure that the requirement you remove will not break the functionality of the remaining requirements."
    elif augmentation_level == AugmentationLevel.CHANGE_REQUIREMENTS:
        augmentation_prompt = f"Here is a generated coding question: {question}. \n generate a similar coding question using the same subject. Change only the enumerated requirements from the original question. Do not change the specified subject or the number of requirements. Your new question should implement the same subject as the original question, just with a new set of requirements. Ensure your new requirements are distinct from the original."
    elif augmentation_level == AugmentationLevel.CHANGE_ANIMATION_OBJECT:
        if topic == Topics.SCIENCE:
            augmentation_prompt = f"Here is a generated coding question: {question}. \n Generate a new coding question similar to the original, but with a similar science experiment that is different from the original. "
        elif topic == Topics.THREE_D:
            augmentation_prompt = f"Here is a generated coding question: {question}. \n Generate a new coding question similar to the original, but with a 2D visualization instead of 3D. Adapt the requirements as necessary to suit your 2D constraints."
        else:
            augmentation_prompt = f"Here is a generated coding question: {question}. \n change the subject of the question to a different related subject such that rest of the question does not need to be modified. The new subject should be distinct from the original one, yet share enough characteristics such that the requirements still make sense. ie. If the original subject is a house with a requirements of windows, the new subject should be something that could feasibly also have windows. The new subject should be as similar to the original as possible, whilst still being distinguishable. As much as possible, please retain the requirements of the question."
    elif augmentation_level == AugmentationLevel.ORIGINAL:
        langfuse_context.update_current_observation(
            metadata={
                "topic": topic,
                "question": question,
                "augmentation_level": augmentation_level,
            }
        )
        return question

    kwargs = {
        "response_model": CodingQuestion,
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": preamble + "\n <user>" + augmentation_prompt + "</user>",
            }
        ],
        "temperature": 0.0,
        "max_tokens": 8192,
        "top_p": 0.9,
    }

    if model.startswith("openai"):
        kwargs["seed"] = random.randint(0, int(1e9))  # needed for OpenAI
    response_model = await client.chat.completions.create(**kwargs)

    kwargs_clone = kwargs.copy()
    kwargs_clone["response_model"] = kwargs["response_model"].model_json_schema()
    langfuse_context.update_current_observation(
        input=kwargs_clone.pop("messages"),
        model=model,
        output=response_model.model_dump(),
        # usage=log_llm_usage(response_model.usage),
        metadata={
            "topic": topic,
            "question": question,
            "augmentation_level": augmentation_level,
            **kwargs_clone,
        },
    )
    logger.success(f"Original question: {question}")
    logger.success(
        f"Augmented question and level:  {augmentation_level}, {response_model.question}"
    )
    return response_model.question


last_topic = []  # global var used to track last used topic.


def build_single_index_html(ans: CodeAnswer) -> CodeAnswer:
    file_extensions = set(os.path.splitext(file.filename)[1] for file in ans.files)
    logger.debug(f"file extensions: {file_extensions}")
    has_js = ".js" in file_extensions
    has_css = ".css" in file_extensions
    has_html = ".html" in file_extensions

    if not has_html:
        raise ValueError("No HTML file found in the CodeAnswer")

    index_html_file = [
        f for f in ans.files if os.path.splitext(f.filename)[1] == ".html"
    ]
    assert len(index_html_file) == 1
    index_html = index_html_file[0]
    soup = BeautifulSoup(index_html.content, "html.parser")

    # Ensure we have html and head tags
    html_tag = soup.find("html")
    if not html_tag:
        html_tag = soup.new_tag("html")
        soup.append(html_tag)

    head_tag = soup.find("head")
    if not head_tag:
        head_tag = soup.new_tag("head")
        html_tag.insert(0, head_tag)

    body_tag = soup.find("body")
    if not body_tag:
        body_tag = soup.new_tag("body")
        html_tag.append(body_tag)

    if has_css:
        index_css_file = [
            f for f in ans.files if os.path.splitext(f.filename)[1] == ".css"
        ]
        assert len(index_css_file) == 1
        index_css = index_css_file[0]
        style_tag = soup.new_tag("style")
        style_tag.string = index_css.content
        head_tag.append(style_tag)

    if has_js:
        index_js_file = [
            f for f in ans.files if os.path.splitext(f.filename)[1] == ".js"
        ]
        assert len(index_js_file) == 1
        index_js = index_js_file[0]
        script_tag = soup.new_tag("script")
        script_tag.string = index_js.content
        body_tag.append(script_tag)

    # Keep only the HTML file, removing JS and CSS files
    new_files = [
        f for f in ans.files if os.path.splitext(f.filename)[1] not in [".js", ".css"]
    ]
    # Update the content of the HTML file
    for file in new_files:
        if file.filename == "index.html":
            file.content = str(soup)

    return CodeAnswer(
        files=new_files,
        installation_commands=ans.installation_commands,
        additional_notes=ans.additional_notes,
    )


# use trace to avoid double dipping cost logging on nested observations
@observe(as_type="trace")
async def build_prompt_responses_pair(
    language: Language, response_strategy: ResponseStrategy
):
    global used_models
    global last_topic

    client = get_llm_api_client(Provider.OPENROUTER)
    question_model = random.choice(GENERATOR_MODELS)
    used_models = set()

    tasks = []
    answer_models = get_answer_model_ids(response_strategy)

    async def _generate_response(
        model: str,
        question: str,
        level: AugmentationLevel | None = None,
        topic: Topics | None = None,
    ):
        if language == Language.JAVASCRIPT:
            model, result = await generate_answer(
                client, model, question, language, topic=topic
            )

            # TODO remove after testing ensure single index.html file just for now
            ans_with_index_html = build_single_index_html(result)
            html_file = next(
                (
                    file
                    for file in ans_with_index_html.files
                    if file.filename == "index.html"
                ),
                None,
            )
            if html_file:
                pass
            else:
                raise ValueError("No index.html file found in the answer")

            iteration_state, message_history = await code_feedback_loop(
                code=html_file.content
            )
            logger.trace(f"message history: {message_history}")

            # final html file
            final_html = iteration_state.latest_code
            # replace whole CodeAnswer with a single final_html file
            for file in result.files:
                if file.filename == "index.html":
                    file.content = final_html

        elif language == Language.PYTHON:
            model, result = await generate_answer_with_feedback(
                client, model, question, language
            )

        return model, result, level

    # 1. randomly select one topic to be used to generate objects + question
    # using random.choices so I can rig the weighting for testing purposes.
    # if last_topic:
    #     available_topics = [topic for topic in list(Topics) if topic != last_topic]
    # else:
    #     available_topics = list(Topics)
    # selected_topic = random.choices(available_topics, k=1)
    # last_topic = selected_topic

    # change weights accordingly to choose what topic of Tasks to generate.
    # in prod, we should use the above commented out topic selection instead.
    selected_topic = random.choices(
        list(Topics), weights=[0.2, 0.2, 0.2, 0.2, 0.2], k=1
    )
    # 2. generate a question using the topic
    question_prompt, _ = await generate_question(
        client, question_model, language, selected_topic[0]
    )

    assert type(question_prompt) is str

    augmented_prompts = []
    if response_strategy == ResponseStrategy.NO_AUGMENTATION:
        for model in answer_models:
            tasks.append(_generate_response(model, question_prompt))
    elif response_strategy == ResponseStrategy.AUGMENTATION_DETERIORIATE:
        # 3. augment questions
        # if augmenting, use same model for both question and answer generation
        answer_models = question_model
        answer_models = random.choice(ANSWER_MODELS)

        assert type(answer_models) is str

        for level in AugmentationLevel:
            augmented_question = await augment_question(
                client, question_model, question_prompt, level, selected_topic[0]
            )
            augmented_prompts.append(
                {"level": level.name, "question": augmented_question}
            )
            # 4. generate answers as code
            tasks.append(
                _generate_response(
                    answer_models, augmented_question, level, selected_topic[0]
                )
            )

    results: list[
        tuple[str, CodeAnswer | None, AugmentationLevel | None]
    ] = await asyncio.gather(*tasks)

    responses = []
    synthetic_ground_truth: dict[str, int] = {}
    for model, result, level in results:
        if not result:
            logger.info(f"@@@@ offending result: {result}, aug_level: {level}")
            raise RuntimeError("Error generating prompt-response pair")

        if language == Language.JAVASCRIPT:
            result = await parse_code_response(result)

        formatted_files = [
            {
                "filename": file.filename,
                "content": file.content,
                "language": file.language,
            }
            for file in result.files
        ]
        completion_id = str(uuid.uuid4())
        responses.append(
            {
                "model": model,
                "completion": {
                    "files": formatted_files,
                    "installation_commands": result.installation_commands,
                    "additional_notes": result.additional_notes,
                },
                "cid": completion_id,
            }
        )

        if level:
            logger.debug(f"{model=},{completion_id=}, {level=}")
            synthetic_ground_truth[completion_id] = level.value

    return {
        "prompt": question_prompt,
        "responses": responses,
        "ground_truth": synthetic_ground_truth,
        "augmented_prompts": augmented_prompts,
        "topic": selected_topic[0].name,
    }


async def test_generate_questions(language: Language):
    log_data = []
    client = get_llm_api_client(provider=Provider.OPENROUTER)
    selected_topic = random.choices(population=list(Topics), k=1)
    for model in GENERATOR_MODELS:
        result = await generate_question(client, model, language, selected_topic[0])
        if result is None:
            continue
        # unstructure tuple
        question, kwargs = result
        log_data.append({"model": model, "question": question, "kwargs": kwargs})

    print(f"{log_data}")
    # Convert the list of dictionaries to a JSON string
    for data in log_data:
        data["kwargs"].pop("response_model")
    json_data = json.dumps(log_data, indent=4)

    # Write the JSON string to a file
    with open("output.json", "w") as file:
        file.write(json_data)


async def main():
    language = Language("Python")
    responses = await build_prompt_responses_pair(
        language=language, response_strategy=ResponseStrategy.AUGMENTATION_DETERIORIATE
    )
    with open("output.json", "w") as f:
        json.dump(responses, f, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
