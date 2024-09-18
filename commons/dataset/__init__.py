VALIDATOR_MIN_STAKE = 20_000

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
    "openai/o1-mini-2024-09-12",
    # "anthropic/claude-3.5-sonnet",
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
    "openai/o1-mini-2024-09-12",
    # "anthropic/claude-3.5-sonnet",
    # "meta-llama/llama-3.1-405b-instruct",
    # "openai/gpt-4o-mini",
    # "openai/gpt-4o",
    # "mistralai/mistral-7b-instruct-v0.1",
    # "deepseek/deepseek-coder",
]
