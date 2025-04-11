import instructor
from dotenv import load_dotenv
from instructor import Mode
from openai import AsyncOpenAI
from strenum import StrEnum

from commons.config import get_settings

load_dotenv()


class Provider(StrEnum):
    TOGETHER_AI = "togetherai"
    OPENAI = "openai"
    OPENROUTER = "openrouter"


def _get_llm_api_kwargs(provider: Provider) -> dict[str, str]:
    """build kwargs for different llm api providers, due to being able to use
    AsyncOpenAI as the default client

    Args:
        provider (Provider): the provider of the llm api

    Raises:
        ValueError: if the provider is unknown
        ValueError: if any of the api keys or base urls are missing

    Returns:
        dict[str, str]: the kwargs for the llm api provider
    """

    llm_api_settings = get_settings().llm_api
    kwargs = {}
    if provider == Provider.TOGETHER_AI:
        kwargs = {
            "api_key": llm_api_settings.together_api_key.get_secret_value(),
            "base_url": llm_api_settings.together_api_base_url,
        }
    elif provider == Provider.OPENAI:
        kwargs = {
            "api_key": llm_api_settings.openai_api_key.get_secret_value(),
            "base_url": llm_api_settings.openai_api_base_url,
        }
    elif provider == Provider.OPENROUTER:
        kwargs = {
            "api_key": llm_api_settings.openrouter_api_key.get_secret_value(),
            "base_url": llm_api_settings.openrouter_api_base_url,
        }

    if not kwargs:
        raise ValueError(f"Unknown provider specified , provider: {provider}")

    # logger.debug(f"Using llm api provider: {provider}")
    for key, value in kwargs.items():
        if value is None:
            raise ValueError(f"Missing value: {value} for {key}")

    return kwargs


def get_llm_api_client(
    provider: Provider = Provider.OPENROUTER,
) -> instructor.AsyncInstructor:
    """instantiate the llm api client, where the instructor client wraps the
    openai client so that we can easily work with pydantic models without having
    to manually parse the json

    Args:
        provider (Provider): the provider of the llm api

    Returns:
        instructor.AsyncInstructor: the llm api client
    """
    kwargs = _get_llm_api_kwargs(provider)
    return instructor.from_openai(
        AsyncOpenAI(api_key=kwargs["api_key"], base_url=kwargs["base_url"]),
        mode=Mode.MD_JSON,
    )
