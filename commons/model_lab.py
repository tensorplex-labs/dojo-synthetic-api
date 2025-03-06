import asyncio

from dotenv import load_dotenv
from loguru import logger

from commons.dataset.personas import get_random_persona, load_persona_dataset
from commons.llm import get_llm_api_client
from commons.synthetic import (
    build_single_index_html,
    generate_answer,
    generate_question,
)
from commons.types import Topics

load_dotenv()


async def main():
    """
    1. generate a question from each topic
    2. send each question to each model
    3. save all results as a json file

    to-do:
    - merge auto-linting feature from dev branch into this script
    - create a front-end to display results
    - experiment with different instructor clients for different models.

    to run:
    python -m commons.model_lab
    """

    logger.info("Starting standalone synthetic data generation")

    load_persona_dataset()

    client = get_llm_api_client()

    # get model names from openrouter website
    question_model = "anthropic/claude-3.5-sonnet"
    answer_models = [
        "anthropic/claude-3.5-haiku",
        "anthropic/claude-3.5-haiku:beta",
    ]

    try:
        # 1. generate a question from each topic
        questions = []
        for topic in Topics:
            logger.info(f"generating {topic.name} question ...")
            persona = get_random_persona()
            question = await generate_question(client, question_model, topic, persona)
            questions.append({"topic": topic, "question": question})

        # 2. for each question, generate an answer from each model.
        answers = []
        for model in answer_models:
            for q in questions:
                logger.info(
                    f"generating {q['topic'].name} answer with model: {model} ..."
                )
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

                # merge generated index.js into index.html
                ans_with_html = build_single_index_html(ans)
                html_file = next(
                    (
                        file
                        for file in ans_with_html.files
                        if file.filename == "index.html"
                    ),
                    None,
                )
                if html_file:
                    pass
                else:
                    raise ValueError("No index.html file found in the answer")
                ans.files = [
                    file for file in ans.files if file.filename == "index.html"
                ]
                if ans.files:
                    ans.files[0].content = html_file.content
                else:
                    raise ValueError("No index.html file found in the result")

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

        # Save to file for inspection
        import json

        with open("syn-gen-trials.json", "w") as f:
            json.dump(result, f, indent=2)
        logger.info("Results saved to syn-gen-trials.json")

    except Exception as e:
        logger.error(f"Error running model_lab.py: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
