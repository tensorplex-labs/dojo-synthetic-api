import asyncio
import os
import time

from dotenv import load_dotenv
from loguru import logger

from commons.dataset.personas import get_random_persona, load_persona_dataset
from commons.llm import get_llm_api_client
from commons.synthetic import (
    _merge_js_and_html,
    generate_answer,
    generate_question,
)
from commons.types import Topics

load_dotenv()

"""
    model_lab.py
    1. generate a question from each topic
    2. send each question to each model
    3. save all results as a json file

    instructions
    - edit the question_model and answer_models variables with the desired models
    - question_model will be used to generate the question
    - each answer model will generate code for that question.
    - to run the script: python -m commons.model_lab.model_lab
    - output will be saved to whatever is defined in the OUTPUT_FILE variable
"""

# get model names from openrouter website

question_model = "anthropic/claude-3.5-sonnet"
question_model = "deepseek/deepseek-r1:free"
answer_models = [
    # "deepseek/deepseek-r1",
    "deepseek/deepseek-r1:free",
    # "deepseek/deepseek-chat-v3-0324:free",
    # "qwen/qwen2.5-32b-instruct",  # 0.79/M
    # "qwen/qwq-32b",  # 0.12/M in 0.18/M out
    # # "anthropic/claude-3.7-sonnet",
    # # "anthropic/claude-3.5-sonnet",
    # "anthropic/claude-3.5-haiku",
    # "anthropic/claude-3.5-haiku:beta",
]
OUTPUT_FILE = "syn-gen-trials.json"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


async def main():
    logger.info("Starting standalone synthetic data generation")

    load_persona_dataset()

    client = get_llm_api_client()

    try:
        # 1. generate a question from each topic
        questions = []
        for topic in Topics:
            logger.info(f"generating {topic.name} question ...")
            persona = get_random_persona()
            question = await generate_question(client, question_model, topic, persona)
            questions.append({"topic": topic, "question": question})
            # break  # gen 1 question only.

        # 2. for each question, generate an answer from each model.
        answers = []
        for model in answer_models:
            for q in questions:
                logger.info(
                    f"generating {q['topic'].name} answer with model: {model} ..."
                )
                start_time = time.time()
                try:
                    _, ans = await generate_answer(
                        client,
                        model,
                        q["question"],
                        q["topic"],
                        f"{model}_{q['topic']}",
                    )
                except Exception as e:
                    # keep going if an error occurs
                    logger.error(
                        f"Error generating {q['topic'].name} answer with model: {model}: {e}"
                    )
                    continue
                logger.success(
                    f"Generated {q['topic'].name} answer with model: {model} in {time.time() - start_time:.2f} seconds"
                )
                # merge generated index.js into index.html
                ans = _merge_js_and_html(ans)

                answers.append(
                    {
                        "name": f"{model}_{q['topic'].name}",
                        "answer": ans,
                        "question": q["question"],
                    }
                )

        # 3. save answers to file
        result = []
        for ans in answers:
            # Convert each CodeAnswer to dict and add to result list
            result.append(
                {
                    "files": [
                        {
                            "tag": ans["name"],
                            "filename": file.filename,
                            "content": file.content,
                            "language": file.language,
                            "question": ans["question"],
                        }
                        for file in ans["answer"].files
                    ]
                }
            )

        # Save to file in the current directory
        output_path = os.path.join(CURRENT_DIR, OUTPUT_FILE)
        import json

        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        logger.info(f"Results saved to {output_path}")

    except Exception as e:
        logger.error(f"Error running model_lab.py: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
