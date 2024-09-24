import os

from dotenv import find_dotenv, load_dotenv
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

load_dotenv(find_dotenv(".env"))

# TODO continue adding all differrent configs here


# we use this instead of the Field(..., env=...) due to some errors in resolving
# the env variables from pydantic, also due to some pyright parsing issues
class LangfuseSettings(BaseSettings):
    public_key: SecretStr = Field(default=os.getenv("LANGFUSE_PUBLIC_KEY", ""))
    secret_key: SecretStr = Field(default=os.getenv("LANGFUSE_SECRET_KEY", ""))
    host: str = Field(default="https://us.cloud.langfuse.com")


class RedisSettings(BaseSettings):
    host: str = Field(default=os.getenv("REDIS_HOST", "localhost"))
    port: int = Field(default=int(os.getenv("REDIS_PORT", "6379")))
    username: str = Field(default=os.getenv("REDIS_USERNAME", "default"))
    password: SecretStr = Field(default=os.getenv("REDIS_PASSWORD", ""))


class LlmApiSettings(BaseSettings):
    together_api_key: SecretStr = Field(default=os.getenv("TOGETHER_API_KEY", ""))
    together_api_base_url: str = Field(default="https://api.together.xyz/v1")
    openai_api_key: SecretStr = Field(default=os.getenv("OPENAI_API_KEY", ""))
    openai_api_base_url: str = Field(default="https://api.openai.com/v1")
    openrouter_api_key: SecretStr = Field(default=os.getenv("OPENROUTER_API_KEY", ""))
    openrouter_api_base_url: str = Field(default="https://openrouter.ai/api/v1")


class Settings(BaseSettings):
    langfuse: LangfuseSettings = LangfuseSettings()
    redis: RedisSettings = RedisSettings()
    llm_api: LlmApiSettings = LlmApiSettings()

    class Config:
        extra = "forbid"
        case_sensitive = True


def get_settings() -> Settings:
    return Settings()


GENERATOR_MODELS = [
    # COMMENTED OUT THESE MODELS BECAUSE NOT WORKING / NOT STABLE
    # "openai/gpt-3.5-turbo",
    # "openai/gpt-3.5-turbo-0125",
    # "openai/gpt-3.5-turbo-1106",
    # "openai/gpt-3.5-turbo-0613",
    # "openai/gpt-3.5-turbo-0301",
    # "openai/gpt-3.5-turbo-16k",
    # "openai/gpt-3.5-turbo-instruct",
    # "google/gemini-pro-1.5",
    # "perplexity/pplx-7b-online",
    # "perplexity/pplx-70b-chat",
    # "mistralai/mistral-7b-instruct-v0.1", cannot use as hits max token limit
    # "deepseek/deepseek-coder",  not good at generating prompts
    # Testing models
    # "openai/gpt-4o-mini",
    # "openai/gpt-4o",
    # "openai/gpt-4-turbo",
    # "openai/o1-preview-2024-09-12",
    # "openai/o1-mini-2024-09-12",
    "anthropic/claude-3.5-sonnet",
    # "meta-llama/llama-3.1-405b-instruct",
    # WORKING MODELS
    # "openai/gpt-4-turbo-preview",
    # "openai/gpt-4-1106-preview",
    # "openai/gpt-4",
    # "openai/gpt-4-0314",
    # "openai/gpt-4-32k",
    # "openai/gpt-4-32k-0314",
    # "openai/gpt-4-vision-preview",
    # "openai/gpt-4o",
    # TODO need to integrate deepseek API provider
    # "deepseek-chat",
]

ANSWER_MODELS = [
    # "phind/phind-codellama-34b",
    # "codellama/codellama-70b-instruct",
    # "mistralai/mixtral-8x22b-instruct",
    # "openai/gpt-4o",
    # "openai/gpt-4-turbo-2024-04-09",
    # "openai/gpt-4-1106-preview",
    # "openai/gpt-3.5-turbo-1106",
    # "anthropic/claude-3-opus-20240229",
    # "anthropic/claude-3-sonnet-20240229",
    # "anthropic/claude-3-haiku-20240307",
    # "google/gemini-pro-1.0",
    # Models that do not with instructor currently
    # "meta-llama/llama-3-70b-instruct",
    # "meta-llama/llama-3-8b-instruct",
    # "mistralai/mistral-large",
    # "google/gemini-pro-1.5",
    # "cognitivecomputations/dolphin-mixtral-8x7b",
    # "cohere/command-r-plus",
    # "openai/o1-preview-2024-09-12",
    # "openai/o1-mini-2024-09-12",
    "anthropic/claude-3.5-sonnet",
    # "meta-llama/llama-3.1-405b-instruct",
    # "openai/gpt-4o-mini",
    # "openai/gpt-4o",
    # "mistralai/mistral-7b-instruct-v0.1",
    # "deepseek/deepseek-coder",
]
