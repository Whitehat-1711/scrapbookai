"""
POST /humanize — Humanization endpoint.
Rewrites AI-generated content to reduce AI detection.
"""

from fastapi import APIRouter, HTTPException

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

        return {
            "humanized_content": humanized_content,
            "before_detection": ai_detection_before,
            "after_detection": ai_detection_after,
            "was_humanized": was_humanized,
            "naturalness_improvement": naturalness_improvement,
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[HUMANIZE ERROR] {error_trace}")
        error_msg = str(e) if str(e) else f"Humanization failed: {type(e).__name__}"
        raise HTTPException(status_code=500, detail=error_msg)
