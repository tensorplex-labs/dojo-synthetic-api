import asyncio
import json
import os
import random
import traceback
import uuid
from enum import Enum
from typing import Dict, List, Tuple, cast

import instructor
from dotenv import load_dotenv
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tenacity import (
    AsyncRetrying,
    RetryError,
    stop_after_attempt,
)

from commons.dataset import ANSWER_MODELS, GENERATOR_MODELS
from commons.executor.python_executor import PythonExecutor
from commons.executor.utils import ExecutionError
from commons.llm.openai_proxy import (
    Provider,
    get_instructor_client,
)
from commons.prompt_builders import (
    Language,
    additional_notes_for_question_prompt,
    build_code_answer_prompt,
    build_code_generation_question_prompt,
    build_python_fix_prompt,
    build_python_review_prompt,
)

load_dotenv()


# define some types
LlmClient = AsyncOpenAI | instructor.AsyncInstructor


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
    content: str = Field(description="Content of the file which can be code or json")
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


async def _generate_objects_to_visualize(
    client: LlmClient, model: str, prev_used_objects: list[str]
):
    class PossibleObjects(BaseModel):
        objects: List[str] = Field(description="List of objects to visualize")

    logger.info(f"Generating objects to use for question with model: {model}")
    kwargs = {
        "response_model": PossibleObjects,
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": f"Please output a valid JSON array containing 30 types of objects (not animal) commonly used for animation coding questions and does not include the following: {', '.join(prev_used_objects)}.",
            }
        ],
        "temperature": random.uniform(0.0, 1.0),
        "max_tokens": 1024,
        "top_p": random.uniform(0.9, 1.0),
    }
    if model.startswith("openai"):
        kwargs["seed"] = random.randint(0, cast(int, 1e9))  # needed for OpenAI
    completion = await client.chat.completions.create(**kwargs)
    logger.success(f"Got objects to visualize, completion={completion=}")
    return completion.objects


used_objects = []
previous_coding_question = ""
used_models = set()


async def generate_question(
    client: instructor.AsyncInstructor, model: str, language: Language
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
                if language == Language.JAVASCRIPT:
                    print("Generating objects to visualize")
                    possible_objects = await _generate_objects_to_visualize(
                        client, model, used_objects
                    )
                    sampled_objects = random.sample(
                        possible_objects, random.randint(3, 5)
                    )
                    used_objects = sampled_objects

                kwargs = {
                    "response_model": CodingQuestion,
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": build_code_generation_question_prompt(
                                random.choices([2, 3, 4], weights=[0.3, 0.5, 0.2])[0],
                                used_objects,
                                previous_coding_question,
                                language,
                            ),
                        }
                    ],
                    "temperature": random.uniform(0.0, 0.5),
                    "max_tokens": 8192,
                    "top_p": random.uniform(0.9, 1.0),
                    "seed": random.randint(0, cast(int, 1e9)),  # needed for OpenAI
                }
                completion: CodingQuestion = await client.chat.completions.create(
                    **kwargs
                )
                coding_question = completion.question
                coding_question = additional_notes_for_question_prompt(
                    coding_question, language
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
        return await generate_question(client, new_model, language)
    except Exception as e:
        print(f"Error occurred while generating question: {e}")

    return None, None


async def generate_answer(
    client: LlmClient,
    model: str,
    question: str,
    language: Language,
    err: str | None = None,
    code: str | None = None,
) -> Tuple[str, CodeAnswer | None]:
    """Generates a coding question answer for a given coding question."""
    import commons.dataset as dataset

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
                question, language.value == Language.JAVASCRIPT
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

    MAX_RETRIES = 5

    # try generating until max retries, then switch models
    try:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(MAX_RETRIES), before_sleep=log_retry_info
        ):
            with attempt:
                completion = await client.chat.completions.create(**kwargs)
                # print(f"Generated completion: {completion}")
                return model, completion
    except RetryError:
        logger.error(
            f"Failed to generate answer after {MAX_RETRIES} attempts. Switching model."
        )
        used_models.add(model)
        remaining_models = [m for m in dataset.ANSWER_MODELS if m not in used_models]
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


async def augment_question(
    client: LlmClient,
    model: str,
    question: str,
    augmentation_level: AugmentationLevel,
) -> str:
    """Augment the question with the given model and augmentation level."""
    logger.info(
        f"Augmenting question with model and augmentation: {model}, {augmentation_level}"
    )
    augmentation_prompt = ""
    if augmentation_level == AugmentationLevel.REMOVE_REQUIREMENTS:
        augmentation_prompt = (
            f"You must remove any 1 requirement from the following question: {question}"
        )
    elif augmentation_level == AugmentationLevel.CHANGE_REQUIREMENTS:
        augmentation_prompt = f"You must change all the requirements from the following question. Do not change the animation object or the number of requirements: {question}"
    elif augmentation_level == AugmentationLevel.CHANGE_ANIMATION_OBJECT:
        augmentation_prompt = f"You must change the animation object from the following question to something else such that rest of the question does not need to be modified. Make sure the new object does not look like the previous object: {question}"
    elif augmentation_level == AugmentationLevel.ORIGINAL:
        return question

    kwargs = {
        "response_model": CodingQuestion,
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": augmentation_prompt,
            }
        ],
        "temperature": random.uniform(0.0, 0.2),
        "max_tokens": 8192,
        "top_p": 0.9,
    }

    if model.startswith("openai"):
        kwargs["seed"] = random.randint(0, int(1e9))  # needed for OpenAI
    completion: CodingQuestion = await client.chat.completions.create(**kwargs)
    logger.success(f"Original question: {question}")
    logger.success(
        f"Augmented question and level:  {augmentation_level}, {completion.question}"
    )
    return completion.question


async def build_prompt_responses_pair(
    language: Language, response_strategy: ResponseStrategy
):
    global used_models

    client = get_instructor_client(Provider.OPENROUTER)
    question_model = random.choice(GENERATOR_MODELS)
    used_models = set()

    tasks = []
    answer_models = get_answer_model_ids(response_strategy)

    async def _generate_response(
        model: str, question: str, level: AugmentationLevel | None = None
    ):
        if language == Language.JAVASCRIPT:
            model, result = await generate_answer(client, model, question, language)
        elif language == Language.PYTHON:
            model, result = await generate_answer_with_feedback(
                client, model, question, language
            )

        return model, result, level

    question_prompt, _ = await generate_question(client, question_model, language)

    if response_strategy == ResponseStrategy.NO_AUGMENTATION:
        for model in answer_models:
            tasks.append(_generate_response(model, question_prompt))
    elif response_strategy == ResponseStrategy.AUGMENTATION_DETERIORIATE:
        # if augmenting, use same model for both question and answer generation
        answer_models = question_model
        assert type(answer_models) is str

        for level in AugmentationLevel:
            augmented_question = await augment_question(
                client, question_model, question_prompt, level
            )
            tasks.append(_generate_response(answer_models, augmented_question, level))

    results: list[
        tuple[str, CodeAnswer | None, AugmentationLevel | None]
    ] = await asyncio.gather(*tasks)

    responses = []
    synthetic_ground_truth: dict[str, int] = {}
    for model, result, level in results:
        if not result:
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
    }


async def test_generate_questions(language: Language):
    log_data = []
    client = get_instructor_client(provider=Provider.OPENROUTER)
    for model in GENERATOR_MODELS:
        result = await generate_question(client, model, language)
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
