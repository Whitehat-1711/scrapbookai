"""
Agent 7 — Internal Linking Agent
──────────────────────────────────
Analyzes blog content + existing blog catalog to suggest
contextually relevant internal links with optimal anchor texts.
"""

# Handle imports with fallback for different module contexts
try:
    from Backend.services.groq_service import chat_completion_json
    from Backend.utils.prompts import internal_linking_prompts
    from Backend.models.response_models import InternalLinkSuggestion, InternalLinkResponse
except ImportError:
    from ..services.groq_service import chat_completion_json
    from ..utils.prompts import internal_linking_prompts
    from ..models.response_models import InternalLinkSuggestion, InternalLinkResponse


async def run_internal_linking(
    content: str,
    existing_blogs: list[dict],
    primary_keyword: str,
) -> InternalLinkResponse:
    """
    Entry point for the Internal Linking Agent.
    Returns InternalLinkResponse with suggestions and a linking score.
    """
    if not existing_blogs:
        return InternalLinkResponse(
            total_suggestions=0,
            suggestions=[],
            linking_score=0.0,
        )

    system, user = internal_linking_prompts(content, existing_blogs, primary_keyword)
    llm_data = await chat_completion_json(system, user, temperature=0.3)

    raw_suggestions = llm_data.get("suggestions", [])
    suggestions = [
        InternalLinkSuggestion(
            anchor_text=s.get("anchor_text", ""),
            target_url=s.get("target_url", ""),
            target_title=s.get("target_title", ""),
            relevance_score=float(s.get("relevance_score", 5.0)),
            placement_hint=s.get("placement_hint", ""),
            reason=s.get("reason", ""),
        )
        for s in raw_suggestions
        if s.get("anchor_text") and s.get("target_url")
    ]

    # Sort by relevance
    suggestions.sort(key=lambda x: x.relevance_score, reverse=True)

    linking_score = float(llm_data.get("linking_score", min(len(suggestions) * 15, 100)))

    return InternalLinkResponse(
        total_suggestions=len(suggestions),
        suggestions=suggestions,
        linking_score=round(linking_score, 1),
    )
