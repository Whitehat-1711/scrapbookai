"""
Agent 6 — Humanization Agent
─────────────────────────────
Rewrites AI-generated blog content to reduce AI detection probability.
Only runs if enable_humanization=True and ai_probability > 45%.
"""

import re

# Handle imports with fallback for different module contexts
try:
    from Backend.services.groq_service import chat_completion
    from Backend.services.ai_detection_service import analyze_ai_probability
    from Backend.utils.prompts import humanization_prompts
    from Backend.models.response_models import AIDetectionResponse
except ImportError:
    from ..services.groq_service import chat_completion
    from ..services.ai_detection_service import analyze_ai_probability
    from ..utils.prompts import humanization_prompts
    from ..models.response_models import AIDetectionResponse


_AI_PHRASE_REPLACEMENTS: list[tuple[str, str]] = [
    (r"\bIn conclusion\b[:,]?\s*", ""),
    (r"\bTo summarize\b[:,]?\s*", ""),
    (r"\bIt is worth noting that\b", "Notably,"),
    (r"\bIt is important to note that\b", "Importantly,"),
    (r"\bIn today's (digital|modern|fast-paced) world\b", "Today"),
    (r"\bDelve into\b", "Explore"),
    (r"\bIn the realm of\b", "In"),
    (r"\bAt the end of the day\b", "Ultimately"),
    (r"\bMoving forward\b", "Next"),
    (r"\bFurthermore\b", "Also"),
    (r"\bMoreover\b", "Plus"),
]


def _preclean_ai_phrases(content: str) -> str:
    cleaned = content
    for pattern, replacement in _AI_PHRASE_REPLACEMENTS:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


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
    precleaned = _preclean_ai_phrases(content)
    flags = ai_detection_result.get("flags", [])

    # Only skip when content is already very human and no AI-style flags were found.
    if ai_prob < 30 and not force and not flags:
        return precleaned, analyze_ai_probability(precleaned)
    system, user = humanization_prompts(precleaned, flags)

    humanized = await chat_completion(
        system,
        user,
        temperature=0.85,
        max_tokens=8000,
        task="humanization",
    )

    # Sometimes LLMs wrap output in code fences; normalize before scoring.
    humanized = humanized.strip()
    if humanized.startswith("```"):
        humanized = humanized.strip("`")
        if humanized.lower().startswith("markdown"):
            humanized = humanized[8:].lstrip()

    # Re-score after humanization
    updated_detection = analyze_ai_probability(humanized)

    # Guardrail: accept the rewrite unless it's materially worse.
    original_prob = float(ai_detection_result.get("ai_probability_percent", 0))
    updated_prob = float(updated_detection.get("ai_probability_percent", 0))
    if updated_prob > (original_prob + 3.0):
        return content, ai_detection_result

    return humanized, updated_detection
