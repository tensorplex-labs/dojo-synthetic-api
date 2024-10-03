import functools
import urllib.parse
from typing import Annotated, List

import aiohttp
from bs4 import BeautifulSoup, Tag
from langfuse.decorators import langfuse_context, observe
from loguru import logger
from openai import AsyncOpenAI

from commons.code_executor import get_feedback
from commons.code_iterator.types import DuckduckgoSearchResult, HtmlCode
from commons.config import get_settings
from commons.llm import get_llm_api_client
from commons.utils.logging import get_kwargs_from_partial

# blacklist domains that are not useful for code fixing
blacklisted_domains = ["reddit.com", "quora.com", "youtube.com"]


async def _browse_result(url: str):
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc
    if any(blacklisted_domain in domain for blacklisted_domain in blacklisted_domains):
        raise Exception(f"Blacklisted domain: {domain}")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")
            text_content = soup.get_text(separator="\n", strip=True)
            return text_content


def _ensure_valid_url(url: str) -> str:
    if not url.startswith("http://") and not url.startswith("https://"):
        if url.startswith("//"):
            url = f"https:{url}"
        else:
            url = f"https://{url}"
    return url


async def _parse_duckduckgo_results(
    html: str, num_top_results: int | None = None
) -> List[DuckduckgoSearchResult]:
    soup = BeautifulSoup(html, "html.parser")
    results = []
    results_div = soup.find("div", class_="serp__results")
    if results_div and isinstance(results_div, Tag):
        for result in results_div.find_all("div", class_="result__body"):
            title_tag = result.find("h2", class_="result__title")
            snippet_tag = result.find("a", class_="result__snippet")
            url_tag = result.find("a", class_="result__url")
            if title_tag and snippet_tag and url_tag:
                title = title_tag.get_text(strip=True)
                snippet = snippet_tag.get_text(strip=True)
                url = url_tag.get_text(strip=True)
                url = _ensure_valid_url(url)
                content = None
                try:
                    content = await _browse_result(url)
                except Exception as e:
                    logger.error(f"Failed to browse {url}: {e}")
                results.append(
                    DuckduckgoSearchResult(
                        title=title, snippet=snippet, url=url, content=content
                    )
                )
            if num_top_results and len(results) == num_top_results:
                break
    else:
        pass

    return results


async def _web_search(search_string: str, num_top_results: int):
    """Perform web search using HTML version of Duckduckgo, because it's free"""
    async with aiohttp.ClientSession() as session:
        safe_search_query = urllib.parse.quote_plus(search_string)
        async with session.get(
            f"https://duckduckgo.com/html/?q={safe_search_query}"
        ) as response:
            content = await response.text()
            return await _parse_duckduckgo_results(content, num_top_results)


# ---------------------------------------------------------------------------- #
#                            LLM FRIENDLY FUNCTIONS                            #
# ---------------------------------------------------------------------------- #


async def web_search_and_format(
    search_string: Annotated[
        str,
        "Search string to query Google with, which should be as specific as possible",
    ],
) -> str:
    """Perform web search and format the results so that an LLM can use the output

    Args:
        search_string (Annotated[ str, "Search string to query Google with, which should be as specific as possible", ]): Search string i.e. "how you like em apples?"

    Returns:
        str: Formatted string that can be used as input to an LLM to interpret
    """
    results = await _web_search(search_string, 3)
    results_str = "\n".join(
        [
            f"Title: {result.title}\nURL: {result.url}\nSnippet: {result.snippet}"
            for result in results
        ]
    )
    return results_str


@observe(as_type="generation", capture_input=False, capture_output=False)
async def call_llm(input: str) -> str | None:
    """Simply use OpenAI as a proxy to call LLMs, no JSON parsing etc, just pure text"""
    try:
        settings = get_settings()
        # simple LLM call without instructor, so we instantiate AsyncOpenAI directly
        client = AsyncOpenAI(
            api_key=settings.llm_api.openrouter_api_key.get_secret_value(),
            base_url=settings.llm_api.openrouter_api_base_url,
        )

        partial_func = functools.partial(
            client.chat.completions.create,
            messages=[{"role": "user", "content": input}],
            model=get_settings().rewoo.tool.use_llm,
        )

        kwargs = get_kwargs_from_partial(partial_func)
        completion = await partial_func()

        completion_text = completion.choices[0].message.content
        langfuse_context.update_current_observation(
            input=kwargs.pop("messages"),
            model=kwargs.pop("model"),
            output=completion_text,
            metadata={
                **kwargs,
            },
        )

        return completion_text
    except Exception as exc:
        logger.error(f"Error while calling tool: LLM, error:{exc}")
        return None


@observe(as_type="generation", capture_input=False, capture_output=False)
async def fix_code(html_code: str) -> str:
    """Fix the code by rendering the HTML code inside the browser to get any runtime errors, then use another LLM call to fix the code.

    Args:
        html_code (str): HTML code to fix

    Returns:
        str: Fixed HTML code
    """
    feedback, modified_code = await get_feedback(html_code)
    if not feedback:
        return html_code

    client = get_llm_api_client()
    # need to provide the modified HTML code with the error logging JS injected
    # so that diagnostics are consistent with the actual lineno/colno error is at
    fix_code_prompt = f"The following is the buggy code: {modified_code}\n\nThe following is the feedback from the execution: {feedback}\n\nYour task is to fix the code and provide the fully working code."

    partial_func = functools.partial(
        client.chat.completions.create,
        messages=[
            {
                "role": "user",
                "content": fix_code_prompt,
            }
        ],
        model=get_settings().rewoo.tool.fix_code,
        response_model=HtmlCode,
    )

    kwargs = get_kwargs_from_partial(partial_func)
    response: HtmlCode = await partial_func()
    langfuse_context.update_current_observation(
        input=kwargs.pop("messages"),
        model=kwargs.pop("model"),
        output=response.model_dump(),
        metadata={
            **kwargs,
        },
    )

    return response.html_code
