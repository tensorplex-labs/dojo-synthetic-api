import urllib.parse
from typing import List

import aiohttp
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel


class DuckduckgoSearchResult(BaseModel):
    title: str
    snippet: str
    url: str
    content: str | None = None


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


def ensure_valid_url(url: str) -> str:
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
                url = ensure_valid_url(url)
                content = None
                try:
                    content = await _browse_result(url)
                except Exception as e:
                    print(f"Failed to browse {url}: {e}")
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


async def web_search(search_string: str, num_top_results: int):
    async with aiohttp.ClientSession() as session:
        safe_search_query = urllib.parse.quote_plus(search_string)
        async with session.get(
            f"https://duckduckgo.com/html/?q={safe_search_query}"
        ) as response:
            content = await response.text()
            return await _parse_duckduckgo_results(content, num_top_results)
