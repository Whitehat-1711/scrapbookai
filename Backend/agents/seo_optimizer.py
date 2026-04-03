"""
Agent 4 — SEO Optimization Agent
──────────────────────────────────
Pure computation — runs all SEO metrics on generated content.
No LLM calls needed here. All deterministic scoring.
"""

from __future__ import annotations

# Handle imports with fallback for different module contexts
try:
    from Backend.utils.seo_utils import (
        compute_keyword_density,
        keyword_in_first_n_words,
        keyword_in_title,
        get_readability_score,
        count_headings,
        extract_lsi_keywords,
        count_internal_links,
        compute_seo_score,
        estimate_traffic_potential,
        count_words,
    )
    from Backend.models.response_models import KeywordDensityDetail, SEOScoreResponse
    from Backend.core.config import KEYWORD_DENSITY_MIN, KEYWORD_DENSITY_MAX
except ImportError:
    from ..utils.seo_utils import (
        compute_keyword_density,
        keyword_in_first_n_words,
        keyword_in_title,
        get_readability_score,
        count_headings,
        extract_lsi_keywords,
        count_internal_links,
        compute_seo_score,
        estimate_traffic_potential,
        count_words,
    )
    from ..models.response_models import KeywordDensityDetail, SEOScoreResponse
    from ..core.config import KEYWORD_DENSITY_MIN, KEYWORD_DENSITY_MAX


def _density_status(density: float) -> str:
    if density < KEYWORD_DENSITY_MIN:
        return "under"
    elif density > KEYWORD_DENSITY_MAX:
        return "over"
    return "optimal"


async def run_seo_analysis(
    content: str,
    title: str,
    keyword: str,
    secondary_keywords: list[str],
    keyword_difficulty: str = "medium",
) -> SEOScoreResponse:
    """
    Runs all SEO checks and returns a SEOScoreResponse.
    """
    word_count = count_words(content)
    readability_score, readability_grade = get_readability_score(content)
    heading_count = count_headings(content)
    internal_link_count = count_internal_links(content)
    lsi_keywords = extract_lsi_keywords(content, keyword)

    kw_in_title = keyword_in_title(title, keyword)
    kw_in_first_100 = keyword_in_first_n_words(content, keyword, 100)

    # Keyword density for primary + secondary
    all_keywords = [keyword] + secondary_keywords
    density_details: list[KeywordDensityDetail] = []

    for kw in all_keywords:
        density = compute_keyword_density(content, kw)
        density_details.append(
            KeywordDensityDetail(
                keyword=kw,
                count=int((density / 100) * word_count),
                density_percent=density,
                status=_density_status(density) if kw == keyword else (
                    "optimal" if 0.2 <= density <= 3.0 else "under"
                ),
            )
        )

    primary_density = density_details[0].density_percent if density_details else 0.0

    # Compute composite SEO score
    overall_score = compute_seo_score(
        word_count=word_count,
        keyword_density=primary_density,
        readability_score=readability_score,
        heading_count=heading_count,
        has_keyword_in_title=kw_in_title,
        has_keyword_in_first_100=kw_in_first_100,
        internal_link_count=internal_link_count,
        lsi_count=len(lsi_keywords),
    )

    # Generate issues and recommendations
    issues, recommendations = _generate_issues_and_recommendations(
        word_count, primary_density, kw_in_title, kw_in_first_100,
        heading_count, internal_link_count, readability_score, lsi_keywords
    )

    traffic_potential = estimate_traffic_potential(overall_score, keyword_difficulty)

    return SEOScoreResponse(
        overall_score=overall_score,
        keyword_density=density_details,
        readability_score=readability_score,
        readability_grade=str(readability_grade),
        word_count=word_count,
        heading_count=heading_count,
        has_meta_structure=True,
        internal_link_count=internal_link_count,
        keyword_in_title=kw_in_title,
        keyword_in_first_100_words=kw_in_first_100,
        lsi_keywords_found=lsi_keywords,
        issues=issues,
        recommendations=recommendations,
        projected_traffic_potential=traffic_potential,
    )


def _generate_issues_and_recommendations(
    word_count, primary_density, kw_in_title, kw_in_first_100,
    heading_count, internal_links, readability_score, lsi_keywords
) -> tuple[list[str], list[str]]:
    issues = []
    recs = []

    if word_count < 1500:
        issues.append(f"Word count ({word_count}) is below 1,500 — thin content risk")
        recs.append("Expand content to at least 2,500 words for competitive keywords")

    if primary_density < KEYWORD_DENSITY_MIN:
        issues.append(f"Primary keyword density ({primary_density}%) is too low")
        recs.append(f"Increase keyword usage to {KEYWORD_DENSITY_MIN}–{KEYWORD_DENSITY_MAX}% density")
    elif primary_density > KEYWORD_DENSITY_MAX:
        issues.append(f"Primary keyword density ({primary_density}%) is too high — stuffing risk")
        recs.append("Reduce keyword repetition and use semantic variations instead")

    if not kw_in_title:
        issues.append("Primary keyword not found in title")
        recs.append("Include primary keyword in the H1 title")

    if not kw_in_first_100:
        issues.append("Primary keyword not in first 100 words")
        recs.append("Mention the primary keyword within the opening paragraph")

    if heading_count < 5:
        issues.append(f"Only {heading_count} headings found — poor content structure")
        recs.append("Add more H2/H3 headings to improve content hierarchy")

    if internal_links < 2:
        issues.append(f"Only {internal_links} internal link(s) found")
        recs.append("Add 3–5 internal links to related blog posts")

    if readability_score < 50:
        issues.append(f"Readability score ({readability_score}) is low")
        recs.append("Simplify sentences, use shorter paragraphs for better readability")

    if len(lsi_keywords) < 5:
        issues.append("Insufficient semantic/LSI keywords")
        recs.append("Include more topic-related terms to improve semantic relevance")

    return issues, recs
