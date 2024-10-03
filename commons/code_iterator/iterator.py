from loguru import logger
from tenacity import AsyncRetrying, RetryError, stop_after_attempt

from commons.code_executor import get_feedback
from commons.code_executor.feedback import _remove_error_logging_js
from commons.code_iterator.rewoo import plan_and_solve
from commons.code_iterator.types import CodeIteration, CodeIterationStates


def parse_code_iteration_state(states: CodeIterationStates) -> CodeIterationStates:
    for state in states.iterations:
        state.code = _remove_error_logging_js(state.code)
        logger.trace("Removed error logging js from code ...")
    return states


async def debug_initial_code(
    initial_html_code: str,
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
    feedback, code_with_loggingjs = await get_feedback(initial_html_code)
    states = CodeIterationStates()
    states.set_initial_state(
        iteration=CodeIteration(code=code_with_loggingjs, error=feedback)
    )
    if not feedback:
        logger.info("⏩ No intitial code executor feedback, skipping feedback loop")
        return parse_code_iteration_state(states)

    if not states.latest_iteration:
        raise ValueError("No initial iteration found")

    while states.current_iteration_num < max_iterations:
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(max_retries_per_iter),
            ):
                with attempt:
                    latest_iteration = states.latest_iteration
                    solution = await plan_and_solve(latest_iteration.code)
                    feedback, code_with_loggingjs = await get_feedback(solution)
                    states.add_iteration(
                        iteration=CodeIteration(
                            code=code_with_loggingjs, error=feedback
                        )
                    )

                    if not feedback:
                        logger.success(
                            f"🚀 No more error feedback found after {states.current_iteration_num}, exiting feedback loop 🙇"
                        )
                        break
        except RetryError as e:
            logger.error(
                f"Failed to generate answer after {max_retries_per_iter} attempts."
            )
            raise e
        except Exception as e:
            logger.error(f"Error occurred while generating code answer: {e}")
            raise e

    return parse_code_iteration_state(states)
