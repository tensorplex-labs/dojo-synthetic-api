import os

import instructor
from dotenv import load_dotenv
from instructor import Mode
from litellm import Router
from loguru import logger
from openai import AsyncOpenAI, OpenAI
from strenum import StrEnum

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_BASE_URL = "https://api.together.xyz/v1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE_URL = "https://api.openai.com/v1"
OPENROUTER_API_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def load_env_series(env_var_name: str):
    # e.g. if we specify OPENAI_API_KEY_1, OPENAI_API_BASE_URL_1, OPENAI_API_KEY_2, OPENAI_API_BASE_URL_2, etc.
    # we can load them all in a loop
    keys = []
    for i in range(1, 100):
        env_var = f"{env_var_name}_{i}"
        key = os.getenv(env_var)
        if key is None or not key:
            break
        keys.append(key)

    if len(keys):
        logger.success(
            f"Loaded {len(keys)} .env for prefix: {env_var_name} for load balancing"
        )

    return keys


def build_openai_models_list(
    models: list[str] = None,
):
    if not models:
        models = [
            "o1-mini",
            "o1-mini-2024-09-12",
            "o1-preview",
            "o1-preview-2024-09-12",
        ]

    model_list = []
    openai_api_keys = load_env_series("OPENAI_API_KEY")
    if len(openai_api_keys) == 0:
        raise ValueError(
            "No OPENAI_API_KEY_1, OPENAI_API_KEY_2, OPENAI_API_KEY_3 ...  found in .env file"
        )
    for model_name in models:
        for api_key in openai_api_keys:
            model_list.append(
                {
                    "model_name": "openai/"
                    + model_name,  # model alias -> loadbalance between models with same `model_name`
                    "litellm_params": {  # params for litellm completion/embedding call
                        "model": model_name,  # actual model name
                        "api_key": api_key,
                        "api_base": OPENAI_API_BASE_URL,
                    },
                    "tpm": 30 * 1e6,
                    "rpm": 20,
                },
            )
    logger.info(f"Built litellm models list for 😈 load balancing 😈\n{model_list}")
    return model_list


class Provider(StrEnum):
    TOGETHER_AI = "togetherai"
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    DEEPSEEK = "deepseek"


def get_openai_kwargs(provider: Provider):
    if provider == Provider.TOGETHER_AI:
        return {"api_key": TOGETHER_API_KEY, "base_url": TOGETHER_API_BASE_URL}
    elif provider == Provider.OPENAI:
        return {"api_key": OPENAI_API_KEY, "base_url": OPENAI_API_BASE_URL}
    elif provider == Provider.OPENROUTER:
        return {"api_key": OPENROUTER_API_KEY, "base_url": OPENROUTER_API_BASE_URL}
    raise ValueError(f"Unknown provider specified , provider: {provider}")


def get_async_openai_client(provider: Provider):
    kwargs = get_openai_kwargs(provider)
    return AsyncOpenAI(api_key=kwargs["api_key"], base_url=kwargs["base_url"])


def get_instructor_client(provider: Provider):
    if not load_env_series("OPENAI_API_KEY"):
        kwargs = get_openai_kwargs(provider)
        return instructor.from_openai(
            AsyncOpenAI(api_key=kwargs["api_key"], base_url=kwargs["base_url"]),
            mode=Mode.MD_JSON,
        )

    # load balancing config
    redis_user = os.getenv("REDIS_USERNAME", "default")
    redis_password = os.getenv("REDIS_PASSWORD")
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_url = f"redis://{redis_user}:{redis_password}@{redis_host}:6379"
    model_list = build_openai_models_list()
    router = Router(
        model_list=model_list,
        redis_url=redis_url,
        routing_strategy="least-busy",
        enable_pre_call_checks=True,  # enables router rate limits for concurrent calls
        default_litellm_params={
            "acompletion": True
        },  # 👈 IMPORTANT - tells litellm to route to async completion function.
    )
    client = instructor.apatch(
        router,
        mode=Mode.MD_JSON,
    )

    return client


def get_sync_openai_client(provider: Provider):
    # known_providers = [provider.value for provider in Provider]
    # TODO @dev use instructor when bittensor migrates to pydantic v2
    # if provider in known_providers:
    #     return instructor.apatch(
    #         AsyncOpenAI(**get_openai_kwargs(provider)), mode=instructor.Mode.MD_JSON
    #     )
    kwargs = get_openai_kwargs(provider)
    return OpenAI(api_key=kwargs["api_key"], base_url=kwargs["base_url"])
