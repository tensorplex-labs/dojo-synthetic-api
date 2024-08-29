import os

import instructor
from dotenv import load_dotenv
from instructor import Mode
from openai import AsyncOpenAI
from strenum import StrEnum

load_dotenv()
# import instructor

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_BASE_URL = "https://api.together.xyz/v1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE_URL = "https://api.openai.com/v1"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE_URL = "https://openrouter.ai/api/v1"


class Provider(StrEnum):
    TOGETHER_AI = "togetherai"
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    DEEPSEEK = "deepseek"


def get_llm_provider_kwargs(provider: Provider):
    if provider == Provider.TOGETHER_AI:
        return {"api_key": TOGETHER_API_KEY, "base_url": TOGETHER_API_BASE_URL}
    elif provider == Provider.OPENAI:
        return {"api_key": OPENAI_API_KEY, "base_url": OPENAI_API_BASE_URL}
    elif provider == Provider.OPENROUTER:
        return {"api_key": OPENROUTER_API_KEY, "base_url": OPENROUTER_API_BASE_URL}
    raise ValueError(f"Unknown provider specified , provider: {provider}")


def get_async_openai_client(provider: Provider):
    kwargs = get_llm_provider_kwargs(provider)
    return AsyncOpenAI(api_key=kwargs["api_key"], base_url=kwargs["base_url"])


def get_instructor_client(provider: Provider):
    kwargs = get_llm_provider_kwargs(provider)
    return instructor.from_openai(
        AsyncOpenAI(api_key=kwargs["api_key"], base_url=kwargs["base_url"]),
        mode=Mode.MD_JSON,
    )
