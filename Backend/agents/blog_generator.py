"""
Agent 3 — Blog Generation Agent
─────────────────────────────────
Generates a full SEO blog using Groq LLM, guided by SERP analysis
and keyword cluster data.
"""

import re
from typing import Any
from slugify import slugify

# Handle imports with fallback for different module contexts
try:
    # When run as uvicorn Backend.core.main:app
    from Backend.services.groq_service import chat_completion, chat_completion_json
    from Backend.utils.prompts import blog_generation_prompts, title_meta_prompts
    from Backend.models.response_models import SERPAnalysisResponse, KeywordClusterResponse
except ImportError:
    # Fallback for relative imports
    from ..services.groq_service import chat_completion, chat_completion_json
    from ..utils.prompts import blog_generation_prompts, title_meta_prompts
    from ..models.response_models import SERPAnalysisResponse, KeywordClusterResponse


def calculate_word_count(text: str) -> int:
    """Calculate word count excluding code blocks, meta descriptions, and HTML comments."""
    # Remove code blocks
    cleaned = re.sub(r"```[\s\S]*?```", "", text)
    # Remove HTML comments
    cleaned = re.sub(r"<!--.*?-->", "", cleaned)
    # Remove meta tags
    cleaned = re.sub(r">.*?<", "", cleaned)
    # Split by whitespace and count
    words = cleaned.split()
    return len(words)


async def expand_content_for_word_count(
    keyword: str,
    current_content: str,
    target_word_count: int,
    current_word_count: int,
) -> str:
    """Expand content if it falls short of target word count."""
    shortfall = target_word_count - current_word_count
    
    if shortfall < 200:  # If within 200 words, accept it
        return current_content
    
    expansion_prompt = f"""The blog post is currently {current_word_count} words, but needs to be {target_word_count} words (shortfall: {shortfall} words).

ORIGINAL BLOG:
{current_content}

Expand the blog by approximately {shortfall} words by:
1. Adding more India-specific case studies or examples
2. Expanding existing H2 sections with deeper analysis
3. Adding more detailed explanations with real-world contexts
4. Including more actionable tips or solutions
5. Enhancing existing bullet points with more detail

REQUIREMENTS:
- Keep the exact same structure (don't add new sections)
- Maintain all markdown formatting
- Keep the same tone and style
- DO NOT add new H1, H2, or H3 headings
- Expand within existing sections only
- Preserve the meta description and title
- Preserve all code snippets, tables, and formatting

Return the EXPANDED blog only - no explanations:"""
    
    try:
        expanded = await chat_completion(
            "You are an expert blog expander who adds depth without changing structure.",
            expansion_prompt,
            temperature=0.7,
            max_tokens=10000,
            task="content_expansion",
        )
        return expanded
    except Exception as e:
        print(f"Expansion failed: {e}. Proceeding with current content.")
        return current_content


async def run_blog_generation(
    keyword: str,
    secondary_keywords: list[str],
    target_location: str,
    word_count: int,
    tone: str,
    serp_analysis: SERPAnalysisResponse | None,
    keyword_clusters: KeywordClusterResponse | None,
    internal_links: list[dict],
    title_override: str | None,
    competitor_urls: list[str] = [],
    web_search_data: dict | None = None,
) -> dict:
    """
    Generates the blog post and returns a dict with:
    { title, meta_description, slug, content }
    
    web_search_data: Optional web search results with latest information
    """
    # Extract SERP intelligence
    content_gaps: list[str] = []
    serp_personality = "long-form guide"
    winning_angle = "Comprehensive, India-specific expert guide"
    missing_keywords: list[str] = []
    weak_sections: list[str] = []
    competitor_insights = ""
    web_search_context = ""

    if serp_analysis and not isinstance(serp_analysis, BaseException):
        content_gaps = [g.topic for g in serp_analysis.content_gaps]
        serp_personality = serp_analysis.serp_personality
        winning_angle = serp_analysis.winning_angle
        missing_keywords = serp_analysis.missing_keywords
        weak_sections = serp_analysis.weak_sections
        # Don't override user's word_count selection - respect their choice

    # Include web search context if available
    if web_search_data:
        try:
            from Backend.agents.web_search_agent import format_web_search_context
        except ImportError:
            from .web_search_agent import format_web_search_context
        
        web_search_context = format_web_search_context(web_search_data)

    # Analyze competitor URLs for tone/structure
    if competitor_urls:
        competitor_insights = (
            f"External competitor sources analyzed ({len(competitor_urls)}): "
            f"{', '.join(competitor_urls)}. Learn tone, structure, and topic sequencing from these "
            f"sources without copying language."
        )

    # Generate the blog
    system, user = blog_generation_prompts(
        keyword=keyword,
        secondary_keywords=secondary_keywords,
        location=target_location,
        word_count=word_count,
        tone=tone,
        content_gaps=content_gaps,
        serp_personality=serp_personality,
        winning_angle=winning_angle,
        competitor_gaps=weak_sections,  # Use weak_sections as competitor_gaps
        internal_links=internal_links,
        title=title_override,
        missing_keywords=missing_keywords,
        competitor_insights=competitor_insights,
        web_search_context=web_search_context,  # Include web search data
    )

    content = await chat_completion(
        system,
        user,
        temperature=0.75,
        max_tokens=8000,
        task="blog_generation",
    )

    # Remove any word count reporting the model might have added
    content = re.sub(r"\n?word\s+count:\s*\d+\n?", "", content, flags=re.IGNORECASE)
    content = content.strip()

    # Calculate content word count (excluding meta, code blocks, etc.)
    actual_word_count = calculate_word_count(content)
    min_acceptable = int(word_count * 0.92)  # Must be at least 92% of target
    
    # If content is too short, expand it (aggressive expansion)
    attempts = 0
    max_attempts = 2
    while actual_word_count < min_acceptable and attempts < max_attempts:
        attempts += 1
        shortfall = word_count - actual_word_count
        if shortfall < 200:
            # For small shortfalls we avoid extra LLM calls to keep latency low.
            break
        print(f"⚠️  Attempt {attempts}: Content is {actual_word_count} words (target: {word_count}, shortfall: {shortfall}). Expanding...")
        content = await expand_content_for_word_count(
            keyword=keyword,
            current_content=content,
            target_word_count=word_count,
            current_word_count=actual_word_count,
        )
        actual_word_count = calculate_word_count(content)
        print(f"✓ Expanded to {actual_word_count} words")
    
    if actual_word_count < min_acceptable:
        print(f"⚠️  WARNING: Final word count {actual_word_count} is still below target {word_count}")

    # Extract meta description if embedded in content
    meta_description = ""
    meta_match = re.search(r"META:\s*(.+?)(?:\n|$)", content, re.IGNORECASE)
    if meta_match:
        meta_description = meta_match.group(1).strip().strip('"')

    # Extract H1 title from content
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    extracted_title = title_match.group(1).strip() if title_match else keyword

    # If no meta in content, generate separately
    if not meta_description:
        t_system, t_user = title_meta_prompts(
            keyword, extracted_title, target_location
        )
        try:
            meta_data = await chat_completion_json(
                t_system,
                t_user,
                temperature=0.3,
                max_tokens=600,
                task="meta",
            )
            meta_description = meta_data.get("meta_description", "")
        except Exception:
            meta_description = f"Discover everything about {keyword} in India. Expert guide covering tips, strategies, and tools."

    title = title_override or extracted_title
    slug = slugify(title)

    return {
        "title": title,
        "meta_description": meta_description[:160],
        "slug": slug,
        "content": content,
        "word_count": actual_word_count,
    }


async def run_title_suggestions(
    keyword: str,
    serp_analysis: Any | None = None,
    count: int = 6,
) -> list[str]:
    """Generate 5-6 SEO title suggestions with diverse formats."""
    safe_count = 6 if count > 6 else 5 if count < 5 else count
    clean_keyword = keyword.strip()

    winning_angle = "Practical, SEO-focused guidance that beats existing content"
    serp_personality = "long-form guide"
    recommended_format = "guide"
    gap_topics: list[str] = []

    if serp_analysis:
        try:
            if hasattr(serp_analysis, "winning_angle"):
                winning_angle = getattr(serp_analysis, "winning_angle") or winning_angle
                serp_personality = getattr(serp_analysis, "serp_personality", serp_personality)
                recommended_format = getattr(serp_analysis, "recommended_format", recommended_format)
                raw_gaps = getattr(serp_analysis, "content_gaps", []) or []
                gap_topics = [getattr(g, "topic", "") for g in raw_gaps if getattr(g, "topic", "")]
            elif isinstance(serp_analysis, dict):
                winning_angle = serp_analysis.get("winning_angle") or winning_angle
                serp_personality = serp_analysis.get("serp_personality") or serp_personality
                recommended_format = serp_analysis.get("recommended_format") or recommended_format
                raw_gaps = serp_analysis.get("content_gaps") or []
                gap_topics = [g.get("topic", "") for g in raw_gaps if isinstance(g, dict) and g.get("topic")]
        except Exception:
            pass

    gaps_text = ", ".join(gap_topics[:4]) if gap_topics else "None provided"

    system = """You are a senior SEO strategist and CTR copywriter.
Create high-converting blog titles for ranking and clicks.
Return only valid JSON."""

    user = f"""Generate exactly {safe_count} blog title suggestions for keyword: \"{clean_keyword}\".

Context:
- SERP personality: {serp_personality}
- Recommended format: {recommended_format}
- Winning angle: {winning_angle}
- Content gaps: {gaps_text}

Rules:
- Every title must contain the exact keyword phrase \"{clean_keyword}\".
- Keep titles engaging and SEO-friendly (ideally 50-70 chars, allow slight variation).
- Ensure diverse formats across the set:
  1) listicle
  2) ultimate guide
  3) question-based
  4) comparison or vs format
  5) actionable/how-to variant
  6) trend/future-focused variant
- Avoid repetitive phrasing and generic clickbait.

Return JSON only in this schema:
{{
  \"titles\": [\"...\", \"...\"]
}}"""

    fallback_titles = [
        f"10 Proven {clean_keyword} Strategies for Faster Growth",
        f"The Ultimate Guide to {clean_keyword} in 2026",
        f"What Is the Best {clean_keyword} Approach for Your Business?",
        f"{clean_keyword} vs Traditional SEO: What Actually Works?",
        f"How to Build a Winning {clean_keyword} Plan Step by Step",
        f"{clean_keyword} Trends to Watch: What Changes Next",
    ]

    try:
        llm_data = await chat_completion_json(system, user, temperature=0.6, max_tokens=1200)
        raw_titles = llm_data.get("titles", []) if isinstance(llm_data, dict) else []

        normalized: list[str] = []
        seen: set[str] = set()
        for item in raw_titles:
            if not isinstance(item, str):
                continue
            title = item.strip().strip('"').strip()
            if not title:
                continue
            if clean_keyword.lower() not in title.lower():
                title = f"{title}: {clean_keyword}"
            key = title.lower()
            if key in seen:
                continue
            seen.add(key)
            normalized.append(title)

        if len(normalized) >= 5:
            return normalized[:safe_count]
    except Exception as e:
        print(f"⚠️  Title suggestion generation failed: {e}")

    return fallback_titles[:safe_count]
