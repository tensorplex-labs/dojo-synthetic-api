import asyncio
import json
import os
import random
import re
import traceback
from typing import Dict, List, Optional, Tuple, cast

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

from commons.dataset import GENERATOR_MODELS
from commons.dataset.prompt_builders import (
    Language,
    additional_notes_for_question_prompt,
    build_code_answer_prompt,
    build_code_generation_question_prompt,
    build_python_fix_prompt,
    build_python_review_prompt,
)
from commons.interpreter import fix_code
from commons.llm.openai_proxy import (
    Provider,
    get_instructor_client,
)
from commons.utils.python_executor import PythonExecutor
from commons.utils.utils import ExecutionError

load_dotenv()


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
    additional_notes: Optional[str] = Field(
        description="Any additional notes or comments about the code solution"
    )


class ErrorAnswer(BaseModel):
    error: str = Field(description="The problem in the code solution")
    solution: str = Field(
        description="The solution to the problem in the code solution"
    )
    changes: Optional[str] = Field(
        description="Any changes that can be made to the code solution to fit the requirements"
    )
    reasoning: Optional[str] = Field(
        description="The reasoning behind the solution to the problem in the code solution"
    )


async def parse_code_response(result_object: CodeAnswer) -> CodeAnswer:
    """Ensure that necessary files appended for python and javascript"""
    result_object = await append_codesandbox_files(result_object)
    # result_object = escape_double_quotes_in_files(result_object)
    return result_object


def escape_double_quotes_in_files(codeanswer_object: CodeAnswer) -> CodeAnswer:
    """Escapes double quotes in the content of each file in the CodeAnswer object."""
    for file in codeanswer_object.files:
        if "content" in file.model_dump():
            file.content = re.sub(r'(?<!\\)"', r"\"", file.content)
            file.content = file.content.replace(r"\'", r"'")
    return codeanswer_object


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
    javascript_file_detected = any(
        file.language.lower() == "javascript" for file in codeanswer_object.files
    )
    python_file_detected = any(
        file.language.lower() == "python" for file in codeanswer_object.files
    )
    if javascript_file_detected:
        return handle_javascript_files(codeanswer_object)
    elif python_file_detected:
        return await handle_python_files(codeanswer_object)
    else:
        return codeanswer_object


async def _generate_objects_to_visualize(
    client: instructor.AsyncInstructor, model: str, prev_used_objects: list[str]
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
) -> tuple[Optional[str], Optional[Dict]]:
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
                completion = await client.chat.completions.create(**kwargs)
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
        return await generate_question(client, new_model)
    except Exception as e:
        print(f"Error occurred while generating question: {e}")

    return None, None


async def generate_answer(
    client: AsyncOpenAI | instructor.AsyncInstructor,
    model: str,
    question: str,
    langauge: Language,
    err: str | None = None,
    code: str | None = None,
) -> Tuple[str, Optional[CodeAnswer]]:
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
                question, langauge.value == Language.JAVASCRIPT
            ),
        },
    ]

    if err and code:
        err_prompt = await generate_python_fix_prompt(client, model, code, err, question)
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
        kwargs["seed"] = random.randint(0, 1e9)  # needed for OpenAI

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
        return await generate_answer(client, new_model, question)
    except Exception as e:
        print(f"Error occurred while generating code answer: {e}")

    return model, None


async def generate_python_fix_prompt(
    client: AsyncOpenAI | instructor.AsyncInstructor,
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


async def build_2_prompt_responses_pairs():
    import commons.dataset as dataset

    client = get_instructor_client(Provider.OPENROUTER)
    # use these models because we can specify seed
    model_choice = random.choice(dataset.GENERATOR_MODELS)
    prompt, kwargs = await generate_question(client, model_choice)
    if not prompt or not kwargs:
        logger.info("Failed to generate question...")
        return []

    # NOTE @dev LLMs here were selected to be able to compare against the EvalPLus leaderboard
    # randomly sampled from pool of models
    answer_models = dataset.ANSWER_MODELS
    num_answer_models = int(os.getenv("NUM_ANSWER_MODELS", 4))
    selected_models = random.sample(
        answer_models, min(num_answer_models, len(answer_models))
    )

    prompt_responses_pairs = []
    for enable_agent_code_fix in [True, False]:
        results: List[Tuple[str, CodeAnswer]] = await asyncio.gather(
            *[
                generate_answer(client, ans_model, prompt)
                for ans_model in selected_models
            ]
        )

        # parse code responses
        responses = []
        for model, result in results:
            if not result:
                continue
            # result = parse_code_response(result)
            if enable_agent_code_fix:
                supported_languages = ["javascript"]
                for i, file in enumerate(result.files):
                    if file.language.lower() not in supported_languages:
                        continue
                    lang, fixed_code = await fix_code(file.content, model)
                    if fixed_code:
                        result.files[i].content = fixed_code

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
        prompt_responses_pairs.append(
            {
                "prompt": prompt
                + "\n[DEBUGGING] Is agent code fix enabled? "
                + str(enable_agent_code_fix),
                "responses": responses,
            }
        )
    return prompt_responses_pairs


async def generate_answer_with_feedback(
    client: AsyncOpenAI | instructor.AsyncInstructor,
    model: str,
    question: str,
    language: Language,
) -> Tuple[str, CodeAnswer | None]:
    previous_code = None
    err = None
    while True:
        model, result = await generate_answer(
            client, model, question, language, previous_code, err
        )
        if result is None:
            return model, None

        try:
            # print("executing")
            return model, await parse_code_response(result)
        except ExecutionError as e:
            err = e.err
            previous_code = e.code


async def build_prompt_responses_pair(language: Language, generator_model=None):
    import commons.dataset as dataset

    global used_models

    client = get_instructor_client(Provider.OPENROUTER)
    # use these models because we can specify seed
    model_choice = generator_model or random.choice(dataset.GENERATOR_MODELS)
    # initialise to empty set
    used_models = set()
    prompt, kwargs = await generate_question(client, model_choice, language)
    if not prompt or not kwargs:
        logger.info("Failed to generate question...")
        raise RuntimeError("Error generating prompt-response pair")
        # return None

    # NOTE @dev LLMs here were selected to be able to compare against the EvalPLus leaderboard
    # randomly sampled from pool of models
    answer_models = dataset.ANSWER_MODELS
    num_answer_models = int(os.getenv("NUM_ANSWER_MODELS", 4))
    selected_models = random.sample(
        answer_models, min(num_answer_models, len(answer_models))
    )

    # check if enough answer models are specified
    if len(answer_models) < num_answer_models:
        logger.warning(
            f"Number of answer models is less than the specified number of models: {num_answer_models}"
        )
        raise RuntimeError("Error generating prompt-response pair")

    # initialise to empty set
    used_models = set()
    tasks = []
    for ans_model in selected_models:
        if language == Language.JAVASCRIPT:
            tasks.append(generate_answer(client, ans_model, prompt, language))
        elif language == Language.PYTHON:
            tasks.append(
                generate_answer_with_feedback(client, ans_model, prompt, language)
            )

    results: List[Tuple[str, CodeAnswer]] = await asyncio.gather(tasks)

    # parse code responses
    responses = []
    for model, result in results:
        if not result:
            raise RuntimeError("Error generating prompt-response pair")

        if language == Language.JAVASCRIPT:
            result = parse_code_response(result)
        # supported_languages = ["javascript", "html"]
        # for i, file in enumerate(result.files):
        #     if file.language.lower() not in supported_languages:
        #         continue
        #     lang, fixed_code = await fix_code(file.content, model)
        #     if fixed_code:
        #         result.files[i].content = fixed_code

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
    language = Language("Javascript")
    responses = await build_prompt_responses_pair(language=language)
    with open("output.json", "w") as f:
        json.dump(responses, f, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
