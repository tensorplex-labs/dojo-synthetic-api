from loguru import logger
from pydantic import BaseModel, Field
from tenacity import AsyncRetrying, RetryError, stop_after_attempt

from commons.code_executor import get_feedback
from commons.code_iterator.prompts import ITERATOR_PROMPT
from commons.llm import get_llm_api_client


class CodeIteration(BaseModel):
    code: str
    error: str
    actions: str = Field(
        default="",
        description="The actions required to be taken to fix any errors in code.",
    )
    thoughts: str = Field(
        default="",
        description="Thoughts and reasoning for the actions taken and code written.",
    )


class CodeIterationStates(BaseModel):
    iterations: list[CodeIteration] = []
    current_iteration_num: int = 0

    def add_iteration(self, iteration: CodeIteration):
        self.iterations.append(iteration)
        self.current_iteration_num += 1

    @property
    def latest_iteration(self) -> CodeIteration | None:
        return self.iterations[-1] if self.iterations else None


def _build_messages_single_turn(iteration: CodeIteration):
    return [
        {
            "role": "system",
            "content": ITERATOR_PROMPT,
        },
        {
            "role": "user",
            "content": f"""
Given Code:
{iteration.code}

Execution Error:
{iteration.error}

Actions to take to fix the code:
{iteration.actions}

Thoughts and reasoning for the actions taken and code written:
{iteration.thoughts}

Fixed Code:
            """,
        },
    ]


async def debug_initial_code(
    initial_html_code: str,
    model: str,
    max_iterations: int = 3,
    max_retries_per_iter: int = 3,
) -> CodeIterationStates:
    """Based on an initial piece of code, perform CoT loop to fix any errors with the code.

    Args:
        initial_code (str): Initial code to debug.
        model (str): Model to use for debugging.
        max_iterations (int, optional): Maximum number of iterations to perform. Defaults to 3.
        max_retries_per_iter (int, optional): Maximum number of retries per iteration. Defaults to 3.

    Raises:
        ValueError: If no initial iteration is found.
        RetryError: If the maximum number of retries is reached.
        Exception: If an error occurs while generating code.

    Returns:
        CodeIterationStates: States of all code iterations.
    """
    feedback = await get_feedback(initial_html_code)
    logger.info(f"Initial feedback: {feedback}")
    states = CodeIterationStates()
    states.add_iteration(
        iteration=CodeIteration(code=initial_html_code, error=feedback)
    )

    kwargs = {
        "response_model": CodeIteration,
        "model": model,
        "temperature": 0.0,
        "max_tokens": 16384,
    }

    if not states.latest_iteration:
        raise ValueError("No initial iteration found")

    client = get_llm_api_client()
    while states.current_iteration_num < max_iterations and feedback:
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(max_retries_per_iter),
            ):
                with attempt:
                    latest_iteration = states.latest_iteration
                    messages = _build_messages_single_turn(latest_iteration)

                    kwargs["messages"] = messages
                    completion: CodeIteration = await client.chat.completions.create(
                        **kwargs
                    )
                    logger.info(f"Completion: {completion}")
                    feedback = await get_feedback(completion.code)
                    states.add_iteration(iteration=completion)

                    if not feedback:
                        break
        except RetryError as e:
            logger.error(
                f"Failed to generate answer after {max_retries_per_iter} attempts."
            )
            raise e
        except Exception as e:
            logger.error(f"Error occurred while generating code answer: {e}")
            raise e

    return states
