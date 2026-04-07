"""
Scraper utility — fetches DuckDuckGo HTML SERP results + individual page content.
No API key needed. Falls back gracefully on network errors.
"""

import re
import asyncio
import aiohttp
from urllib.parse import quote_plus, unquote, urlparse, parse_qs
from bs4 import BeautifulSoup

# Handle imports with fallback for different module contexts
try:
    from Backend.core.config import SCRAPER_TIMEOUT, MAX_SERP_RESULTS, SERPAPI_KEY
except ImportError:
    from ..core.config import SCRAPER_TIMEOUT, MAX_SERP_RESULTS, SERPAPI_KEY


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


async def _fetch(session: aiohttp.ClientSession, url: str, timeout: int = SCRAPER_TIMEOUT) -> str:
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
            if resp.status == 200:
                return await resp.text()
    except Exception:
        pass
    return ""


def _normalize_duckduckgo_link(link: str) -> str:
    if not link:
        return ""
    if link.startswith("//duckduckgo.com/l/") or "duckduckgo.com/l/?" in link:
        parsed = urlparse(link if link.startswith("http") else f"https:{link}")
        uddg = parse_qs(parsed.query).get("uddg", [])
        if uddg:
            return unquote(uddg[0])
    return link


async def _get_serp_results_serpapi(keyword: str, max_results: int) -> list[dict]:
    if not SERPAPI_KEY:
        return []
    query = quote_plus(keyword.strip())
    url = (
        "https://serpapi.com/search.json"
        f"?engine=google&q={query}&api_key={SERPAPI_KEY}&num={max_results}&hl=en&gl=in"
    )
    try:
        timeout = aiohttp.ClientTimeout(total=SCRAPER_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
    except Exception:
        return []

    organic = data.get("organic_results", []) if isinstance(data, dict) else []
    parsed = []
    for item in organic[:max_results]:
        link = str(item.get("link", "")).strip()
        title = str(item.get("title", "")).strip()
        snippet = str(item.get("snippet", "")).strip()
        if not link or not title:
            continue
        parsed.append(
            {
                "title": title,
                "url": link,
                "snippet": snippet,
                "display_url": str(item.get("displayed_link", link)),
            }
        )
    return parsed


async def _get_serp_results_ddg_html(keyword: str, max_results: int) -> list[dict]:
    query = quote_plus(keyword.strip())
    url = f"https://html.duckduckgo.com/html/?q={query}&kl=in-en"
    async with aiohttp.ClientSession() as session:
        html = await _fetch(session, url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    results = []
    for result in soup.select(".result__body")[:max_results]:
        title_tag = result.select_one(".result__title a")
        snippet_tag = result.select_one(".result__snippet")
        url_tag = result.select_one(".result__url")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = _normalize_duckduckgo_link(title_tag.get("href", ""))
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
        display_url = url_tag.get_text(strip=True) if url_tag else link
        if title and link:
            results.append({"title": title, "url": link, "snippet": snippet, "display_url": display_url})
    return results


async def _get_serp_results_ddg_lite(keyword: str, max_results: int) -> list[dict]:
    query = quote_plus(keyword.strip())
    url = f"https://lite.duckduckgo.com/lite/?q={query}"
    async with aiohttp.ClientSession() as session:
        html = await _fetch(session, url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    results = []
    links = soup.select("a[href]")
    for a in links:
        href = str(a.get("href", "")).strip()
        title = a.get_text(strip=True)
        if not href or not title:
            continue
        if "duckduckgo.com/y.js" in href or href.startswith("/"):
            continue
        link = _normalize_duckduckgo_link(href)
        if not link.startswith("http"):
            continue
        results.append(
            {
                "title": title,
                "url": link,
                "snippet": "",
                "display_url": link,
            }
        )
        if len(results) >= max_results:
            break
    return results


async def get_serp_results(keyword: str, max_results: int = MAX_SERP_RESULTS) -> list[dict]:
    """
    Scrape DuckDuckGo for top organic results.
    Returns list of { title, url, snippet }.
    """
    keyword = (keyword or "").strip()
    if not keyword:
        return []
    providers = [
        _get_serp_results_serpapi,
        _get_serp_results_ddg_html,
        _get_serp_results_ddg_lite,
    ]
    for provider in providers:
        try:
            data = await provider(keyword, max_results)
            if data:
                return data
        except Exception:
            continue
    return []


async def fetch_page_text(url: str) -> dict:
    """
    Download a URL and return its cleaned body text, headings, and keywords.
    Used to estimate competitor word counts and extract topics.
    Returns dict with 'text', 'headings', 'keywords', 'topics'.
    """
    async with aiohttp.ClientSession() as session:
        html = await _fetch(session, url, timeout=15)

    if not html:
        return {"text": "", "headings": [], "keywords": [], "topics": []}

    soup = BeautifulSoup(html, "lxml")

    # Remove scripts, styles, nav, footer
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    # Extract headings
    headings = []
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        headings.append({
            'level': int(tag.name[1]),
            'text': tag.get_text(strip=True)
        })

    # Prefer article / main body
    body = soup.find("article") or soup.find("main") or soup.find("body")
    if body:
        text = " ".join(body.get_text(separator=" ").split())
    else:
        text = " ".join(soup.get_text(separator=" ").split())

    # Extract keywords: high-frequency words
    import re
    from collections import Counter
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())  # Words longer than 3 chars
    common_words = [word for word, _ in Counter(words).most_common(20)]

    # Extract topics: from headings and common phrases
    topics = [h['text'] for h in headings if len(h['text']) > 5]
    # Add some topic extraction from text (simple: noun phrases or key sentences)
    # For now, use headings as topics

    return {
        "text": text,
        "headings": headings,
        "keywords": common_words,
        "topics": topics
    }


async def fetch_multiple_pages(urls: list[str]) -> list[dict]:
    """Concurrently fetch multiple pages and return detailed content."""
    tasks = [fetch_page_text(url) for url in urls]
    return await asyncio.gather(*tasks)
