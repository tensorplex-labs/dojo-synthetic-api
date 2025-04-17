def get_hf_prompt(base_prompt: str, base_code: str, feedback: str) -> str:
    hf_prompt = f"""
        <system>
            Here is the code that you must improve upon:
            <base_code>
                {base_code}
            </base_code>

            Here is the prompt that was used to generate <base_code>
            <base_prompt>
                {base_prompt}
            </base_prompt>

            <role>
                You are an expert software engineer. Your job is to improve

                Improve <base_code> according to the following user feedback: <feedback> {feedback} </feedback>

                Refer to <base_prompt> and <base_code> to assist you.
            </role>
        </system>

    """
    return hf_prompt
