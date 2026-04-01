"""
POST /keywords/cluster — Standalone keyword clustering endpoint.
GET  /keywords/suggest — Quick keyword suggestions for a seed term.
"""

from fastapi import APIRouter, HTTPException

# Handle imports with fallback for different module contexts
try:
    # When run as: uvicorn backend.core.main:app
    from backend.models.request_models import KeywordClusterRequest
    from backend.models.response_models import KeywordClusterResponse
    from backend.agents.keyword_agent import run_keyword_clustering
except ImportError:
    # Fallback for relative imports
    from ..models.request_models import KeywordClusterRequest
    from ..models.response_models import KeywordClusterResponse
    from ..agents.keyword_agent import run_keyword_clustering

router = APIRouter(prefix="/keywords", tags=["Keyword Intelligence"])


@router.post("/cluster", response_model=KeywordClusterResponse)
async def cluster_keywords(req: KeywordClusterRequest):
    """
    Cluster a seed keyword into intent-based groups with
    traffic estimates and difficulty scores.
    """
    import logging
    logger = logging.getLogger("blogy")
    try:
        return await run_keyword_clustering(
            seed_keyword=req.seed_keyword,
            target_location=req.target_location,
            cluster_count=req.cluster_count,
        )
    except Exception as e:
        logger.error(f"Keyword clustering error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Keyword clustering failed: {str(e)}")


@router.get("/suggest")
async def suggest_keywords(seed: str, location: str = "India"):
    """
    Quick endpoint — returns flat list of keyword suggestions
    without full cluster analysis.
    """
    try:
        result = await run_keyword_clustering(
            seed_keyword=seed,
            target_location=location,
            cluster_count=3,
        )
        all_keywords = []
        for cluster in result.clusters:
            all_keywords.extend(cluster.keywords)
        return {
            "seed": seed,
            "suggestions": list(dict.fromkeys(all_keywords)),  # deduplicate, preserve order
            "recommended_primary": result.recommended_primary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword suggestion failed: {str(e)}")
