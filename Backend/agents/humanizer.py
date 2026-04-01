"""
Agent 6 — Humanization Agent
─────────────────────────────
Rewrites AI-generated blog content to reduce AI detection probability.
Only runs if enable_humanization=True and ai_probability > 45%.
"""

# Handle imports with fallback for different module contexts
try:
    from backend.services.groq_service import chat_completion
    from backend.services.ai_detection_service import analyze_ai_probability
    from backend.utils.prompts import humanization_prompts
    from backend.models.response_models import AIDetectionResponse
except ImportError:
    from ..services.groq_service import chat_completion
    from ..services.ai_detection_service import analyze_ai_probability
    from ..utils.prompts import humanization_prompts
    from ..models.response_models import AIDetectionResponse


async def run_humanization(
    content: str,
    ai_detection_result: dict,
    force: bool = False,
) -> tuple[str, dict]:
    """
    Entry point for the Humanization Agent.

    Returns:
        (humanized_content, updated_ai_detection_dict)
    
    Skips humanization if:
    - ai_probability < 45% AND force=False
    """
    ai_prob = ai_detection_result.get("ai_probability_percent", 0)

    if ai_prob < 45 and not force:
        # Already human-enough, skip
        return content, ai_detection_result

    flags = ai_detection_result.get("flags", [])
    system, user = humanization_prompts(content, flags)

    humanized = await chat_completion(system, user, temperature=0.85, max_tokens=8000)

    # Sometimes LLMs wrap output in code fences; normalize before scoring.
    humanized = humanized.strip()
    if humanized.startswith("```"):
        humanized = humanized.strip("`")
        if humanized.lower().startswith("markdown"):
            humanized = humanized[8:].lstrip()

    # Re-score after humanization
    updated_detection = analyze_ai_probability(humanized)

    # Guardrail: never return a version with a worse AI probability score.
    original_prob = float(ai_detection_result.get("ai_probability_percent", 0))
    updated_prob = float(updated_detection.get("ai_probability_percent", 0))
    if updated_prob >= original_prob:
        return content, ai_detection_result

    return humanized, updated_detection
