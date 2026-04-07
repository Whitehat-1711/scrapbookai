"""
Agent — Web Search Integration
─────────────────────────────────
Fetches real-time web content for recent topics.
Extracts key insights, statistics, and latest information.
"""

from __future__ import annotations

import asyncio
import re
from collections import Counter
from datetime import datetime

try:
    from Backend.utils.scraper import get_serp_results, fetch_multiple_pages
    from Backend.services.groq_service import chat_completion_json
except ImportError:
    from ..utils.scraper import get_serp_results, fetch_multiple_pages
    from ..services.groq_service import chat_completion_json


async def run_web_search(
    keyword: str,
    max_results: int = 8,
    extract_insights: bool = True,
) -> dict:
    """
    Performs a web search and extracts key insights for blog generation.
    
    Returns:
    {
        "keyword": "...",
        "search_date": "2026-04-07",
        "results_count": 8,
        "search_results": [
            {"title": "...", "url": "...", "snippet": "...", "summary": "..."}
        ],
        "key_insights": [
            "Insight 1...",
            "Insight 2...",
            ...
        ],
        "trending_topics": ["topic1", "topic2", ...],
        "statistics": ["stat1", "stat2", ...],
        "key_sources": ["source1", "source2", ...],
    }
    """
    
    print(f"🔍 Searching web for: {keyword}")
    
    # Step 1: Get SERP results
    serp_results = await get_serp_results(keyword, max_results=max_results)
    
    if not serp_results:
        print(f"⚠️  No search results found for: {keyword}")
        return {
            "keyword": keyword,
            "search_date": datetime.now().strftime("%Y-%m-%d"),
            "results_count": 0,
            "search_results": [],
            "key_insights": [],
            "trending_topics": [],
            "statistics": [],
            "key_sources": [],
        }
    
    print(f"✓ Found {len(serp_results)} results")
    
    # Step 2: Fetch page content from top results
    urls_to_fetch = [r["url"] for r in serp_results[:5]]
    page_contents = await fetch_multiple_pages(urls_to_fetch)
    
    # Step 3: Extract insights if requested
    key_insights = []
    trending_topics = []
    statistics = []
    
    if extract_insights and page_contents:
        try:
            key_insights, trending_topics, statistics = await _extract_insights(
                keyword=keyword,
                search_results=serp_results[:5],
                page_contents=page_contents,
            )
        except Exception as e:
            print(f"⚠️  Insight extraction failed: {e}")
    
    # Step 4: Compile key sources
    key_sources = [r["display_url"] for r in serp_results[:4]]
    
    return {
        "keyword": keyword,
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "results_count": len(serp_results),
        "search_results": [
            {
                "title": r["title"],
                "url": r["url"],
                "snippet": r["snippet"],
                "summary": r["snippet"][:200],  # First 200 chars as summary
            }
            for r in serp_results
        ],
        "key_insights": key_insights,
        "trending_topics": trending_topics,
        "statistics": statistics,
        "key_sources": key_sources,
    }


async def _extract_insights(
    keyword: str,
    search_results: list[dict],
    page_contents: list[dict],
) -> tuple[list[str], list[str], list[str]]:
    """
    Use LLM to extract key insights, trends, and statistics from search results.
    """
    
    # Format search results for LLM
    results_text = "\n".join([
        f"- {r['title']}: {r['snippet']}"
        for r in search_results[:5]
    ])
    
    # Format page content summaries
    content_text = "\n---\n".join([
        f"Source: {pc.get('url', 'Unknown')}\nContent: {pc.get('text', '')[:500]}"
        for pc in page_contents[:3]
        if pc.get('text')
    ])
    
    system = """You are an expert content analyst. Extract:
1. Key Insights: 3-5 important takeaways from the search results
2. Trending Topics: 3-5 related topics gaining traction
3. Statistics: 3-5 important numbers/statistics mentioned

Return ONLY valid JSON with no markdown or explanation."""
    
    user = f"""Keyword: "{keyword}"

SEARCH RESULTS:
{results_text}

PAGE CONTENT:
{content_text}

Extract insights in this JSON format:
{{
  "key_insights": [
    "Insight 1 (1-2 sentences)...",
    "Insight 2..."
  ],
  "trending_topics": [
    "Topic 1",
    "Topic 2"
  ],
  "statistics": [
    "X% of users... (source: ...)",
    "N companies... (source: ...)"
  ]
}}"""
    
    try:
        result = await chat_completion_json(system, user, temperature=0.3)
        
        return (
            result.get("key_insights", [])[:5],
            result.get("trending_topics", [])[:5],
            result.get("statistics", [])[:5],
        )
    except Exception as e:
        print(f"⚠️  LLM extraction failed: {e}")
        return [], [], []


def format_web_search_context(web_search_data: dict) -> str:
    """
    Format web search data as context for blog generation prompt.
    """
    if not web_search_data:
        return ""
    
    lines = [
        f"📅 Latest Information (searched {web_search_data['search_date']}):",
        "",
    ]
    
    if web_search_data.get("key_insights"):
        lines.append("Key Insights:")
        for insight in web_search_data["key_insights"][:3]:
            lines.append(f"- {insight}")
        lines.append("")
    
    if web_search_data.get("statistics"):
        lines.append("Important Statistics:")
        for stat in web_search_data["statistics"][:3]:
            lines.append(f"- {stat}")
        lines.append("")
    
    if web_search_data.get("trending_topics"):
        lines.append("Related Trending Topics:")
        lines.append(", ".join(web_search_data["trending_topics"][:5]))
        lines.append("")
    
    if web_search_data.get("key_sources"):
        lines.append("Primary Sources:")
        for source in web_search_data["key_sources"][:3]:
            lines.append(f"- {source}")
    
    return "\n".join(lines)
