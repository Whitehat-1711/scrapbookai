"""
Agent 2 — SERP Gap Analysis Agent
────────────────────────────────────
1. Scrapes DuckDuckGo for top results
2. Fetches competitor page text concurrently
3. Sends everything to Groq for gap analysis
4. Returns structured data for UI (gaps + keywords + insights)
"""

from __future__ import annotations

import asyncio
import re
from collections import Counter

# Handle imports with fallback for different module contexts
try:
    from backend.utils.scraper import get_serp_results, fetch_multiple_pages
    from backend.services.groq_service import chat_completion_json
    from backend.utils.prompts import serp_gap_prompts
    from backend.models.response_models import SERPResult, SERPGap, SERPAnalysisResponse
    from backend.core.config import MAX_SERP_RESULTS
except ImportError:
    from ..utils.scraper import get_serp_results, fetch_multiple_pages
    from ..services.groq_service import chat_completion_json
    from ..utils.prompts import serp_gap_prompts
    from ..models.response_models import SERPResult, SERPGap, SERPAnalysisResponse
    from ..core.config import MAX_SERP_RESULTS


def _detect_content_type(title: str, snippet: str) -> str:
    combined = (title + " " + snippet).lower()
    if any(w in combined for w in ["best", "top", "list", "ways", "tips"]):
        return "listicle"
    if any(w in combined for w in ["how to", "guide", "tutorial", "step"]):
        return "guide"
    if any(w in combined for w in ["vs", "versus", "compare", "comparison"]):
        return "comparison"
    if "?" in title:
        return "qa"
    return "long-form"


_STOP_WORDS = {
    "that", "with", "have", "this", "will", "your", "from", "they", "know", "want",
    "been", "good", "much", "some", "time", "very", "when", "come", "here", "just",
    "like", "long", "make", "many", "over", "such", "take", "than", "them", "well",
    "were", "what", "where", "which", "about", "into", "while", "using", "used",
    "into", "also", "their", "there", "these", "those", "because", "could", "would",
    "should", "after", "before", "under", "being", "does", "doing", "done", "each",
}


def _tokenize_terms(text: str) -> list[str]:
    return re.findall(r"\b[a-z][a-z0-9\-]{2,}\b", (text or "").lower())


def _expand_expected_keyword_space(keyword: str, coverage_map: dict) -> list[str]:
    base_tokens = [t for t in _tokenize_terms(keyword) if t not in _STOP_WORDS]
    keyword_phrase = keyword.strip().lower()
    common_modifiers = [
        "guide", "strategy", "best practices", "mistakes", "checklist", "framework",
        "examples", "case studies", "tools", "comparison", "benefits", "cost",
        "implementation", "workflow", "template", "metrics",
    ]
    expected = {keyword_phrase}
    for token in base_tokens:
        expected.add(token)
    for modifier in common_modifiers:
        expected.add(f"{keyword_phrase} {modifier}")
        for token in base_tokens:
            expected.add(f"{token} {modifier}")
    for topic in coverage_map.get("topics", [])[:25]:
        normalized = re.sub(r"\s+", " ", (topic or "").strip().lower())
        if normalized and 4 <= len(normalized) <= 80:
            expected.add(normalized)
    return list(expected)


def _compute_missing_keywords(keyword: str, page_data: list[dict], coverage_map: dict, llm_keywords: list[str]) -> list[str]:
    candidate_keywords = [k.strip() for k in llm_keywords if isinstance(k, str) and k.strip()]
    if len(candidate_keywords) >= 5:
        return candidate_keywords[:8]

    expected_space = _expand_expected_keyword_space(keyword, coverage_map)
    combined_text = " ".join([d.get("text", "") for d in page_data if d.get("text")])
    tokens = [t for t in _tokenize_terms(combined_text) if t not in _STOP_WORDS]
    token_freq = Counter(tokens)
    heading_text = " ".join(h.get("text", "") for d in page_data for h in d.get("headings", []))
    heading_tokens = set(_tokenize_terms(heading_text))
    competitor_covered = set(k.lower() for k in coverage_map.get("keywords", []))
    competitor_covered.update(heading_tokens)

    gaps: list[str] = []
    for phrase in expected_space:
        phrase_tokens = [t for t in _tokenize_terms(phrase) if t not in _STOP_WORDS]
        if not phrase_tokens:
            continue
        coverage_score = sum(token_freq.get(t, 0) for t in phrase_tokens)
        covered_ratio = sum(1 for t in phrase_tokens if t in competitor_covered) / len(phrase_tokens)
        # Gaps = low absolute coverage and weak distribution in headings/keywords.
        if coverage_score <= 3 or covered_ratio < 0.4:
            normalized = " ".join(phrase.split())
            if normalized and normalized not in gaps:
                gaps.append(normalized)

    # Add high-signal terms from weakly represented tokens as fallback.
    if len(gaps) < 5:
        for term, _ in token_freq.most_common(60):
            if term in _STOP_WORDS or term in keyword.lower().split():
                continue
            if term not in competitor_covered:
                gaps.append(term)
            if len(gaps) >= 8:
                break

    if len(gaps) < 5:
        generic = ["implementation guide", "best practices", "common mistakes", "cost breakdown", "case studies"]
        for g in generic:
            if g not in gaps:
                gaps.append(g)

    return gaps[:8]


def _compute_weak_sections(keyword: str, coverage_map: dict, llm_sections: list[str]) -> list[str]:
    sections = [s.strip() for s in llm_sections if isinstance(s, str) and s.strip()]
    if len(sections) >= 3:
        return sections[:6]

    headings_text = " ".join(coverage_map.get("headings", [])).lower()
    expected_sections = [
        "Implementation Challenges",
        "Cost and ROI Analysis",
        "Real-world Case Studies",
        "Common Mistakes",
        "Maintenance and Scalability",
        "Risk and Compliance",
    ]
    if "guide" in keyword.lower():
        expected_sections = [
            "Step-by-Step Implementation",
            "Troubleshooting Checklist",
            "Advanced Optimization",
            "Common Deployment Issues",
            "Performance Benchmarks",
        ]
    weak = []
    for sec in expected_sections:
        sec_tokens = [t for t in _tokenize_terms(sec) if t not in _STOP_WORDS]
        if not sec_tokens:
            continue
        if not any(t in headings_text for t in sec_tokens):
            weak.append(sec)
    if not weak:
        weak = expected_sections[:3]
    return weak[:6]


def _build_content_gap_summary(keyword: str, missing_keywords: list[str], weak_sections: list[str], llm_summary: dict | None) -> dict:
    if isinstance(llm_summary, dict):
        title = (llm_summary.get("title") or "").strip()
        description = (llm_summary.get("description") or "").strip()
        if title and description:
            return {"title": title, "description": description}

    top_kws = ", ".join(missing_keywords[:3])
    top_sections = ", ".join(weak_sections[:2])
    return {
        "title": f"The {keyword.title()} Depth Gap",
        "description": (
            f"Competitors under-cover high-intent themes like {top_kws}. "
            f"They are also shallow on {top_sections}. Building these sections with practical depth is a direct ranking opportunity."
        ),
    }


async def run_serp_analysis(
    keyword: str,
    target_location: str = "India",
    max_results: int = MAX_SERP_RESULTS,
    competitor_urls: list[str] | None = None,  # type: ignore
) -> SERPAnalysisResponse:
    """
    Entry point for the SERP Gap Analysis Agent.
    """

    # ─────────────────────────────────────────────
    # Step 1: Fetch SERP results
    # ─────────────────────────────────────────────
    try:
        raw_results = await get_serp_results(keyword, max_results)
        if not raw_results:
            raise ValueError(f"No SERP results found for keyword: {keyword}")
    except Exception as e:
        raise Exception(f"Failed to fetch SERP results: {str(e)}")

    # ─────────────────────────────────────────────
    # Step 2: Build SERPResult objects
    # ─────────────────────────────────────────────
    serp_results = []
    for i, r in enumerate(raw_results):
        serp_results.append(
            SERPResult(
                rank=i + 1,
                title=r["title"],
                url=r["url"],
                snippet=r["snippet"],
                word_count_estimate=0,
                has_featured_snippet=(i == 0),
                content_type=_detect_content_type(r["title"], r["snippet"]),
            )
        )

    # ─────────────────────────────────────────────
    # Step 3: Fetch competitor pages with detailed analysis
    # ─────────────────────────────────────────────
    try:
        urls_to_fetch = [r.url for r in serp_results[:10]]
        if competitor_urls:
            urls_to_fetch = list(set(urls_to_fetch + competitor_urls))[:8]
        
        page_data = await fetch_multiple_pages(urls_to_fetch)
        if not page_data:
            raise ValueError("Failed to fetch any competitor pages")
    except Exception as e:
        raise Exception(f"Failed to fetch competitor pages: {str(e)}")

    # Update word counts and extract competitor coverage
    competitor_headings = []
    competitor_keywords = set()
    competitor_topics = set()

    for i, data in enumerate(page_data):
        text = data.get("text", "")
        headings = data.get("headings", [])
        keywords = data.get("keywords", [])
        topics = data.get("topics", [])

        if i < len(serp_results):
            serp_results[i].word_count_estimate = len(text.split()) if text else 500

        competitor_headings.extend([h['text'] for h in headings if h.get("text")])
        competitor_keywords.update(keywords)
        competitor_topics.update(topics)

    avg_word_count = (
        sum(r.word_count_estimate for r in serp_results if r.word_count_estimate)
        // max(1, sum(1 for r in serp_results if r.word_count_estimate))
    )

    # Build combined coverage map
    coverage_map = {
        "headings": list(set(competitor_headings))[:120],
        "keywords": list(competitor_keywords)[:200],
        "topics": list(competitor_topics)[:120],
    }

    # ─────────────────────────────────────────────
    # Step 4: Enhanced LLM gap analysis with competitor data
    # ─────────────────────────────────────────────
    raw_data = [
        {"title": r.title, "snippet": r.snippet, "url": r.url}
        for r in serp_results
    ]

    # Summarize competitor content for LLM
    competitor_summary = "\n".join([
        f"Competitor {i+1}: Headings: {', '.join([h['text'][:50] for h in data.get('headings', [])[:3]])} | Keywords: {', '.join(data.get('keywords', [])[:5])}"
        for i, data in enumerate(page_data[:5]) if data.get('text')
    ])

    system, user = serp_gap_prompts(keyword, raw_data, page_data, competitor_summary, coverage_map)

    llm_data = {}
    try:
        llm_data = await chat_completion_json(system, user, temperature=0.3) or {}
    except Exception as e:
        # Keep pipeline alive with deterministic fallbacks when LLM is unavailable.
        print(f"[SERP] LLM analysis failed, using heuristic fallback: {e}")

    # ─────────────────────────────────────────────
    # Step 5: Extract structured insights
    # ─────────────────────────────────────────────

    # Existing gaps
    gaps = [
        SERPGap(
            topic=g.get("topic", ""),
            importance=g.get("importance", "medium"),
            reason=g.get("reason", ""),
        )
        for g in llm_data.get("content_gaps", [])
    ]

    # ✅ NEW: Missing keywords with enhanced fallback
    missing_keywords = _compute_missing_keywords(
        keyword=keyword,
        page_data=page_data,
        coverage_map=coverage_map,
        llm_keywords=llm_data.get("missing_keywords", []),
    )

    # ✅ NEW: Weak sections with enhanced fallback
    weak_sections = _compute_weak_sections(
        keyword=keyword,
        coverage_map=coverage_map,
        llm_sections=llm_data.get("weak_sections", []),
    )

    # ✅ NEW: Highlight “goldmine” opportunity
    content_gap_summary = _build_content_gap_summary(
        keyword=keyword,
        missing_keywords=missing_keywords,
        weak_sections=weak_sections,
        llm_summary=llm_data.get("content_gap_summary"),
    )

    # ─────────────────────────────────────────────
    # Step 6: Return enriched response
    # ─────────────────────────────────────────────
    return SERPAnalysisResponse(
        keyword=keyword,
        serp_personality=llm_data.get("serp_personality", "long-form"),
        results=serp_results,
        content_gaps=gaps,

        # ✅ NEW FIELDS FOR UI
        missing_keywords=missing_keywords,
        weak_sections=weak_sections,
        content_gap_summary=content_gap_summary,

        average_word_count=avg_word_count or 1200,
        recommended_format=llm_data.get("recommended_format", "long-form guide"),
        recommended_word_count=llm_data.get("recommended_word_count", 2500),
        winning_angle=llm_data.get(
            "winning_angle", "Comprehensive, insight-driven content"
        ),
    )