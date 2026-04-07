"""
Deterministic SEO scoring engine.

This module computes an explainable, SERP-relative SEO score from:
- blog content
- SERP competitor data
- lightweight metadata

No LLM calls, no randomness, no pipeline-step bonuses.
"""

from __future__ import annotations

import re
from typing import Any

import textstat


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _normalize_text(text: str) -> str:
    """Lowercase and collapse whitespace for robust deterministic matching."""
    lowered = _to_text(text).lower()
    return re.sub(r"\s+", " ", lowered).strip()


def _strip_markdown(text: str) -> str:
    cleaned = _to_text(text)
    cleaned = re.sub(r"```[\s\S]*?```", " ", cleaned)
    cleaned = re.sub(r"`[^`]*`", " ", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*[-*+]\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*\d+\.\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", cleaned)
    cleaned = re.sub(r"_{1,3}(.*?)_{1,3}", r"\1", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _count_words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", _strip_markdown(text)))


def _extract_headings(text: str) -> list[str]:
    return [h.strip() for h in re.findall(r"^#{1,6}\s+(.+)$", _to_text(text), re.MULTILINE)]


def _contains_phrase(haystack_normalized: str, phrase: str) -> bool:
    phrase_norm = _normalize_text(phrase)
    if not phrase_norm:
        return False
    pattern = r"\b" + re.escape(phrase_norm) + r"\b"
    return bool(re.search(pattern, haystack_normalized))


def _unique_non_empty(items: list[Any]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        text = _normalize_text(item)
        if not text or text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique


def compute_keyword_score(blog: str, serp_data: dict[str, Any]) -> tuple[float, str]:
    """Keyword Coverage (25 points), with extra weight for top keywords."""
    blog_norm = _normalize_text(_strip_markdown(blog))

    all_keywords = _unique_non_empty(list(serp_data.get("keywords", [])))
    top_keywords = _unique_non_empty(list(serp_data.get("top_keywords", [])))

    if not all_keywords:
        return 0.0, "No competitor keywords provided, so keyword coverage scored as 0."

    matched_keywords = sum(1 for kw in all_keywords if _contains_phrase(blog_norm, kw))
    base_coverage = matched_keywords / len(all_keywords)

    top_coverage = 0.0
    matched_top = 0
    if top_keywords:
        matched_top = sum(1 for kw in top_keywords if _contains_phrase(blog_norm, kw))
        top_coverage = matched_top / len(top_keywords)

    # Extra weight for top keywords while keeping deterministic bounded behavior.
    weighted_coverage = (0.7 * base_coverage) + (0.3 * top_coverage)
    score = _clamp(weighted_coverage * 25.0, 0.0, 25.0)

    explanation = (
        f"Covered {matched_keywords}/{len(all_keywords)} competitor keywords and "
        f"{matched_top}/{len(top_keywords) if top_keywords else 0} top keywords; "
        f"weighted coverage {weighted_coverage:.2f}."
    )
    return round(score, 2), explanation


def compute_depth_score(blog: str, serp_data: dict[str, Any]) -> tuple[float, str]:
    """Content Depth (20 points) relative to SERP average word count."""
    blog_wc = _count_words(blog)
    serp_word_counts = [
        int(wc) for wc in serp_data.get("word_counts", [])
        if isinstance(wc, (int, float)) and wc > 0
    ]

    if not serp_word_counts:
        return 0.0, "No SERP word counts provided, so content depth scored as 0."

    avg_wc = sum(serp_word_counts) / len(serp_word_counts)
    if avg_wc <= 0:
        return 0.0, "Invalid SERP average word count, so content depth scored as 0."

    ratio = blog_wc / avg_wc

    if ratio < 0.7:
        # Scale 0-10 as ratio moves 0.0 -> 0.7
        score = (ratio / 0.7) * 10.0
        band = "below optimal"
    elif ratio <= 1.2:
        # Scale 10-20 as ratio moves 0.7 -> 1.2
        score = 10.0 + ((ratio - 0.7) / 0.5) * 10.0
        band = "optimal"
    elif ratio <= 1.8:
        # Slight penalty from 20 down to 12 as ratio moves 1.2 -> 1.8
        score = 20.0 - ((ratio - 1.2) / 0.6) * 8.0
        band = "slightly over-optimized"
    else:
        # Strong penalty for excessive length; bottoms at 0 around ratio 2.6+
        score = max(0.0, 12.0 - ((ratio - 1.8) / 0.8) * 12.0)
        band = "over-optimized"

    score = _clamp(score, 0.0, 20.0)
    explanation = (
        f"Blog has {blog_wc} words vs SERP average {avg_wc:.0f} "
        f"(ratio {ratio:.2f}, {band})."
    )
    return round(score, 2), explanation


def compute_serp_alignment_score(blog: str, serp_data: dict[str, Any]) -> tuple[float, str]:
    """SERP Alignment (20 points) based on heading/topic overlap."""
    blog_norm = _normalize_text(_to_text(blog))

    serp_headings = _unique_non_empty(list(serp_data.get("headings", [])))
    if not serp_headings:
        return 0.0, "No SERP headings provided, so SERP alignment scored as 0."

    matched_headings = sum(1 for h in serp_headings if _contains_phrase(blog_norm, h))
    alignment = matched_headings / len(serp_headings)
    score = _clamp(alignment * 20.0, 0.0, 20.0)

    explanation = (
        f"Covered {matched_headings}/{len(serp_headings)} key SERP headings "
        f"(alignment {alignment:.2f})."
    )
    return round(score, 2), explanation


def compute_readability_score(blog: str) -> tuple[float, str]:
    """Readability (10 points) using Flesch Reading Ease."""
    plain = _strip_markdown(blog)
    if not plain:
        return 0.0, "Blog content is empty after cleanup, so readability scored as 0."

    fre = float(textstat.flesch_reading_ease(plain))
    fre = _clamp(fre, 0.0, 100.0)

    if 60.0 <= fre <= 75.0:
        score = 10.0
    elif 45.0 <= fre < 60.0:
        # 45 -> 6, 60 -> 10
        score = 6.0 + ((fre - 45.0) / 15.0) * 4.0
    elif 75.0 < fre <= 90.0:
        # 75 -> 10, 90 -> 6
        score = 10.0 - ((fre - 75.0) / 15.0) * 4.0
    elif fre < 45.0:
        # 0 -> 0, 45 -> 6
        score = (fre / 45.0) * 6.0
    else:
        # 90 -> 6, 100 -> 2
        score = 6.0 - ((fre - 90.0) / 10.0) * 4.0

    score = _clamp(score, 0.0, 10.0)
    explanation = f"Flesch Reading Ease is {fre:.1f}; ideal range is 60-75."
    return round(score, 2), explanation


def compute_structure_score(blog: str) -> tuple[float, str]:
    """Structure (10 points) based on deterministic content checks."""
    raw = _to_text(blog)

    has_h1 = bool(re.search(r"^#\s+.+", raw, re.MULTILINE))
    h2_count = len(re.findall(r"^##\s+.+", raw, re.MULTILINE))
    has_multiple_h2 = h2_count >= 2

    paragraphs = [
        p.strip() for p in re.split(r"\n\s*\n", raw)
        if p.strip() and not re.match(r"^#{1,6}\s+", p.strip())
    ]
    paragraph_lengths = [_count_words(p) for p in paragraphs if _count_words(p) > 0]
    avg_paragraph_len = (
        sum(paragraph_lengths) / len(paragraph_lengths)
        if paragraph_lengths else 0.0
    )
    reasonable_paragraphs = 35.0 <= avg_paragraph_len <= 140.0

    has_bullets = bool(re.search(r"^\s*([-*+]\s+|\d+\.\s+)", raw, re.MULTILINE))

    checks = {
        "Has H1": has_h1,
        "Has multiple H2": has_multiple_h2,
        "Paragraph length reasonable": reasonable_paragraphs,
        "Uses bullet/numbered lists": has_bullets,
    }
    passed = sum(1 for ok in checks.values() if ok)
    score = (passed / len(checks)) * 10.0

    passed_labels = [label for label, ok in checks.items() if ok]
    explanation = (
        f"Passed {passed}/{len(checks)} structure checks"
        f" ({'; '.join(passed_labels) if passed_labels else 'none'})."
    )
    return round(score, 2), explanation


def compute_internal_link_score(metadata: dict[str, Any]) -> tuple[float, str]:
    """Internal Linking (10 points) with ideal of 5 links."""
    internal_links = metadata.get("internal_links", 0)
    try:
        internal_links = int(internal_links)
    except (TypeError, ValueError):
        internal_links = 0

    internal_links = max(0, internal_links)
    ideal_links = 5
    score = min(internal_links / ideal_links, 1.0) * 10.0
    explanation = f"Used {internal_links} internal links; ideal target is {ideal_links}."
    return round(score, 2), explanation


def compute_naturalness_score(metadata: dict[str, Any]) -> tuple[float, str]:
    """Naturalness (5 points) from AI probability in range 0-1."""
    ai_probability = metadata.get("ai_probability", 1.0)
    try:
        ai_probability = float(ai_probability)
    except (TypeError, ValueError):
        ai_probability = 1.0

    ai_probability = _clamp(ai_probability, 0.0, 1.0)
    score = (1.0 - ai_probability) * 5.0
    explanation = (
        f"AI probability is {ai_probability:.2f}; lower is better for naturalness."
    )
    return round(score, 2), explanation


def _verdict_from_total(total_score: int) -> str:
    if total_score > 80:
        return "Good"
    if total_score >= 60:
        return "Average"
    return "Needs Improvement"


def compute_seo_score(blog: str, serp_data: dict, metadata: dict) -> dict:
    """
    Deterministic SEO score calculator.

    Returns:
    {
      "total_score": int,
      "breakdown": {
        "keyword_coverage": float,
        "content_depth": float,
        "serp_alignment": float,
        "readability": float,
        "structure": float,
        "internal_linking": float,
        "naturalness": float
      },
      "explanations": { ... },
      "verdict": "Good|Average|Needs Improvement"
    }
    """
    keyword_score, keyword_exp = compute_keyword_score(blog, serp_data)
    depth_score, depth_exp = compute_depth_score(blog, serp_data)
    alignment_score, alignment_exp = compute_serp_alignment_score(blog, serp_data)
    readability_score, readability_exp = compute_readability_score(blog)
    structure_score, structure_exp = compute_structure_score(blog)
    internal_score, internal_exp = compute_internal_link_score(metadata)
    naturalness_score, naturalness_exp = compute_naturalness_score(metadata)

    breakdown = {
        "keyword_coverage": keyword_score,
        "content_depth": depth_score,
        "serp_alignment": alignment_score,
        "readability": readability_score,
        "structure": structure_score,
        "internal_linking": internal_score,
        "naturalness": naturalness_score,
    }

    explanations = {
        "keyword_coverage": keyword_exp,
        "content_depth": depth_exp,
        "serp_alignment": alignment_exp,
        "readability": readability_exp,
        "structure": structure_exp,
        "internal_linking": internal_exp,
        "naturalness": naturalness_exp,
    }

    total_score = int(round(sum(breakdown.values())))
    total_score = int(_clamp(float(total_score), 0.0, 100.0))

    return {
        "total_score": total_score,
        "breakdown": breakdown,
        "explanations": explanations,
        "verdict": _verdict_from_total(total_score),
    }


def test_seo_score() -> None:
    """Simple deterministic smoke test with mock inputs."""
    mock_blog = """
# Technical SEO Audit for SaaS Websites

> META: Learn how to run a technical SEO audit for SaaS sites with practical steps, tools, and fixes that improve crawlability and rankings.

A technical SEO audit helps teams identify crawl, indexation, and performance bottlenecks before they hurt organic growth.

## Crawlability and Indexation Basics
Start by validating robots.txt and XML sitemap coverage.

## Core Web Vitals and Performance
Improve LCP, CLS, and INP by reducing render-blocking assets.

## On-Page Technical Signals
Use canonical tags, schema markup, and clean URL structure.

## Common Technical SEO Mistakes
- Broken internal links
- Duplicate title tags
- Thin pages with no intent match

1. Crawl the site.
2. Prioritize issues by impact.
3. Deploy fixes in batches.
4. Re-crawl and verify.
"""

    mock_serp = {
        "titles": [
            "Technical SEO Audit Checklist for 2026",
            "How to Perform a Technical SEO Audit",
            "Technical SEO Audit: Complete Guide",
        ],
        "headings": [
            "Crawlability",
            "Indexation",
            "Core Web Vitals",
            "Schema Markup",
            "Technical SEO Mistakes",
        ],
        "word_counts": [1600, 1800, 2100, 1700],
        "keywords": [
            "technical seo audit",
            "crawlability",
            "indexation",
            "core web vitals",
            "schema markup",
            "canonical tags",
            "robots.txt",
        ],
        "top_keywords": [
            "technical seo audit",
            "core web vitals",
            "indexation",
        ],
    }

    mock_metadata = {
        "internal_links": 3,
        "ai_probability": 0.22,
    }

    result = compute_seo_score(mock_blog, mock_serp, mock_metadata)
    print("SEO Score Test Result:")
    print(result)


if __name__ == "__main__":
    test_seo_score()
