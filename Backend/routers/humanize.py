"""
POST /humanize — Humanization endpoint.
Rewrites AI-generated content to reduce AI detection.
"""

from fastapi import APIRouter, HTTPException
import re

# Handle imports with fallback for different module contexts
try:
    from Backend.models.request_models import HumanizationRequest
    from Backend.services.ai_detection_service import analyze_ai_probability
    from Backend.agents.humanizer import run_humanization
except ImportError:
    from ..models.request_models import HumanizationRequest
    from ..services.ai_detection_service import analyze_ai_probability
    from ..agents.humanizer import run_humanization

router = APIRouter(prefix="", tags=["Humanization"])


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


@router.post("/humanize")
async def humanize_content(req: HumanizationRequest):
    """
    Analyze content for AI detection, then humanize if needed.

    Returns:
    - humanized_content: The rewritten text
    - before_detection: Detection scores before humanization
    - after_detection: Detection scores after humanization
    - was_humanized: Boolean indicating if humanization was applied
    - naturalness_improvement: Improvement in naturalness score (after - before)
    """
    try:
        # Detect AI in original content
        ai_detection_before = analyze_ai_probability(req.content)

        # Run humanization
        humanized_content, ai_detection_after = await run_humanization(
            content=req.content,
            ai_detection_result=ai_detection_before,
            force=req.force,
        )

        # Determine if humanization actually occurred
        was_humanized = humanized_content != req.content

        # Calculate improvement - ensure both are dicts
        before_naturalness = ai_detection_before.get("naturalness_score", 0) if isinstance(ai_detection_before, dict) else 0
        after_naturalness = ai_detection_after.get("naturalness_score", 0) if isinstance(ai_detection_after, dict) else 0
        naturalness_improvement = after_naturalness - before_naturalness
        ai_probability_delta = (
            (ai_detection_before.get("ai_probability_percent", 0) if isinstance(ai_detection_before, dict) else 0)
            - (ai_detection_after.get("ai_probability_percent", 0) if isinstance(ai_detection_after, dict) else 0)
        )
        before_flags = ai_detection_before.get("flags", []) if isinstance(ai_detection_before, dict) else []
        after_flags = ai_detection_after.get("flags", []) if isinstance(ai_detection_after, dict) else []
        flags_removed_count = max(0, len(before_flags) - len(after_flags))
        input_words = _word_count(req.content)
        output_words = _word_count(humanized_content)
        word_count_delta = output_words - input_words

        return {
            "humanized_content": humanized_content,
            "before_detection": ai_detection_before,
            "after_detection": ai_detection_after,
            "was_humanized": was_humanized,
            "naturalness_improvement": naturalness_improvement,
            "ai_probability_delta": ai_probability_delta,
            "flags_removed_count": flags_removed_count,
            "input_word_count": input_words,
            "output_word_count": output_words,
            "word_count_delta": word_count_delta,
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[HUMANIZE ERROR] {error_trace}")
        error_msg = str(e) if str(e) else f"Humanization failed: {type(e).__name__}"
        raise HTTPException(status_code=500, detail=error_msg)
