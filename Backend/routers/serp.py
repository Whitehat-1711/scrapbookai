"""
POST /serp/analyze — Standalone SERP gap analysis endpoint.
"""

from fastapi import APIRouter, HTTPException

# Handle imports with fallback for different module contexts
try:
    # When run as: uvicorn backend.core.main:app
    from backend.models.request_models import SERPAnalysisRequest
    from backend.models.response_models import SERPAnalysisResponse
    from backend.agents.serp_agent import run_serp_analysis
except ImportError:
    # Fallback for relative imports
    from ..models.request_models import SERPAnalysisRequest
    from ..models.response_models import SERPAnalysisResponse
    from ..agents.serp_agent import run_serp_analysis

router = APIRouter(prefix="/serp", tags=["SERP Analysis"])


@router.post("/analyze", response_model=SERPAnalysisResponse)
async def analyze_serp(req: SERPAnalysisRequest):
    """
    Scrapes top SERP results for a keyword, fetches competitor
    page content, and identifies content gaps using Groq LLM.

    Returns:
    - SERP personality (dominant content format)
    - Content gaps competitors missed
    - Recommended format + word count
    - Winning angle to outrank all results
    """
    try:
        return await run_serp_analysis(
            keyword=req.keyword,
            target_location=req.target_location,
            max_results=req.max_results,
            competitor_urls=req.competitor_urls,
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[SERP ERROR] {error_trace}")
        error_msg = str(e) if str(e) else f"SERP analysis failed: {type(e).__name__}"
        raise HTTPException(status_code=500, detail=error_msg)
