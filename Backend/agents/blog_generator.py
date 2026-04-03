"""
Agent 3 — Blog Generation Agent
─────────────────────────────────
Generates a full SEO blog using Groq LLM, guided by SERP analysis
and keyword cluster data.
"""

import re
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
            system="You are an expert blog expander who adds depth without changing structure.",
            user=expansion_prompt,
            temperature=0.7,
            max_tokens=10000
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
) -> dict:
    """
    Generates the blog post and returns a dict with:
    { title, meta_description, slug, content }
    """
    # Extract SERP intelligence
    content_gaps: list[str] = []
    serp_personality = "long-form guide"
    winning_angle = "Comprehensive, India-specific expert guide"
    missing_keywords: list[str] = []
    weak_sections: list[str] = []
    competitor_insights = ""

    if serp_analysis and not isinstance(serp_analysis, BaseException):
        content_gaps = [g.topic for g in serp_analysis.content_gaps]
        serp_personality = serp_analysis.serp_personality
        winning_angle = serp_analysis.winning_angle
        missing_keywords = serp_analysis.missing_keywords
        weak_sections = serp_analysis.weak_sections
        if word_count < serp_analysis.recommended_word_count:
            word_count = serp_analysis.recommended_word_count

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
    )

    content = await chat_completion(system, user, temperature=0.75, max_tokens=8000)

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
            meta_data = await chat_completion_json(t_system, t_user, temperature=0.3)
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
