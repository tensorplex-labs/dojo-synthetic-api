import os

import instructor
from dotenv import load_dotenv
from instructor import Mode
from loguru import logger
from openai import AsyncOpenAI
from strenum import StrEnum

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_BASE_URL = "https://api.together.xyz/v1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE_URL = "https://api.openai.com/v1"
OPENROUTER_API_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


class Provider(StrEnum):
    TOGETHER_AI = "togetherai"
    OPENAI = "openai"
    OPENROUTER = "openrouter"


def get_llm_api_kwargs(provider: Provider) -> dict[str, str]:
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
    kwargs = {}
    if provider == Provider.TOGETHER_AI:
        kwargs = {"api_key": TOGETHER_API_KEY, "base_url": TOGETHER_API_BASE_URL}
    elif provider == Provider.OPENAI:
        kwargs = {"api_key": OPENAI_API_KEY, "base_url": OPENAI_API_BASE_URL}
    elif provider == Provider.OPENROUTER:
        kwargs = {"api_key": OPENROUTER_API_KEY, "base_url": OPENROUTER_API_BASE_URL}

    if not kwargs:
        raise ValueError(f"Unknown provider specified , provider: {provider}")

    logger.debug(f"Using llm api provider: {provider}")
    for key, value in kwargs.items():
        if value is None:
            raise ValueError(f"Missing value: {value} for {key}")

    return kwargs


def get_llm_api_client(provider: Provider) -> instructor.AsyncInstructor:
    """instantiate the llm api client, where the instructor client wraps the
    openai client so that we can easily work with pydantic models without having
    to manually parse the json

    Args:
        provider (Provider): the provider of the llm api

    Returns:
        instructor.AsyncInstructor: the llm api client
    """
    kwargs = get_llm_api_kwargs(provider)
    return instructor.from_openai(
        AsyncOpenAI(api_key=kwargs["api_key"], base_url=kwargs["base_url"]),
        mode=Mode.MD_JSON,
    )
