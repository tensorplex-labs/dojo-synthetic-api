import functools
import inspect
import os

from loguru import logger
from tenacity import RetryCallState


def log_retry_info(retry_state: RetryCallState):
    """Meant to be used with tenacity's before_sleep callback"""
    exception_str = retry_state.outcome.exception() if retry_state.outcome else ""
    caller_info: str = ""
    try:
        caller_frames = inspect.getouterframes(inspect.currentframe())
        # get the last frame
        caller_frame = caller_frames[-1]

        # extract module name, file name, function name, and line number
        module_name = caller_frame.frame.f_globals.get("__name__", "")
        file_name = os.path.basename(caller_frame.filename)
        function_name = caller_frame.function
        line_no = caller_frame.lineno

        # Format the caller info
        caller_info = f"{module_name}.{file_name}:{function_name}:{line_no}"

        exception_str = retry_state.outcome.exception() if retry_state.outcome else ""
        logger.warning(
            f"Retry attempt {retry_state.attempt_number} failed in {caller_info} with exception: {exception_str}, code context: {caller_frame.code_context}"
        )
        return
    except Exception:
        pass

    logger.warning(
        f"Retry attempt {retry_state.attempt_number} failed in {caller_info} with exception: {exception_str}"
    )


def get_kwargs_from_partial(p: functools.partial) -> dict:
    """Infer the positional & keyword arguments from a partial function (i.e. "pre-filled" function) so that we don't need to keep copying kwargs dictionary for logging, etc.

    Args:
        p (functools.partial): A partial function

    Returns:
        dict: A dictionary of the positional and keyword arguments
    """

    sig = inspect.signature(p.func)

    # map positional args to keyword args
    positional_args_as_kwargs = {
        param.name: arg
        for param, arg in zip(sig.parameters.values(), p.args, strict=False)
    }

    # combine positional and keyword args
    all_kwargs = {**positional_args_as_kwargs, **p.keywords}

    # strip 'openai' from model name if present
    if "model" in all_kwargs:
        all_kwargs["model"] = all_kwargs["model"].replace("openai/", "")

    logger.trace(f"Inferred kwargs from partial: {all_kwargs}")
    return all_kwargs
