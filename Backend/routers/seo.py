"""
POST /seo/analyze     — Full SEO score for existing content.
POST /seo/detect-ai   — AI detection on any text.
POST /seo/snippet     — Featured snippet optimization.
POST /seo/links       — Internal linking suggestions.
"""

from fastapi import APIRouter, HTTPException

# Handle imports with fallback for different module contexts
try:
    # When run as: uvicorn backend.core.main:app
    from backend.models.request_models import (
        SEOAnalysisRequest,
        AIDetectionRequest,
        SnippetOptimizationRequest,
        InternalLinkRequest,
    )
    from backend.models.response_models import (
        SEOScoreResponse,
        AIDetectionResponse,
        SnippetOptimizationResponse,
        InternalLinkResponse,
    )
    from backend.agents.seo_optimizer import run_seo_analysis
    from backend.agents.snippet_agent import run_snippet_optimization
    from backend.agents.internal_linking_agent import run_internal_linking
    from backend.services.ai_detection_service import analyze_ai_probability
except ImportError:
    # Fallback for relative imports
    from ..models.request_models import (
        SEOAnalysisRequest,
        AIDetectionRequest,
        SnippetOptimizationRequest,
        InternalLinkRequest,
    )
    from ..models.response_models import (
        SEOScoreResponse,
        AIDetectionResponse,
        SnippetOptimizationResponse,
        InternalLinkResponse,
    )
    from ..agents.seo_optimizer import run_seo_analysis
    from ..agents.snippet_agent import run_snippet_optimization
    from ..agents.internal_linking_agent import run_internal_linking
    from ..services.ai_detection_service import analyze_ai_probability

router = APIRouter(prefix="/seo", tags=["SEO Analysis"])


@router.post("/analyze", response_model=SEOScoreResponse)
async def analyze_seo(req: SEOAnalysisRequest):
    """
    Run a full SEO audit on provided content.

    Checks:
    - Keyword density (primary + secondary)
    - Readability score (Flesch-Kincaid)
    - Heading structure
    - Internal links
    - Keyword placement (title, first 100 words)
    - LSI / semantic keywords
    - Overall SEO score (0-100)
    - Projected traffic potential
    """
    try:
        return await run_seo_analysis(
            content=req.content,
            title=req.content.split("\n")[0].replace("#", "").strip(),
            keyword=req.keyword,
            secondary_keywords=req.secondary_keywords,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SEO analysis failed: {str(e)}")


@router.post("/detect-ai", response_model=AIDetectionResponse)
async def detect_ai(req: AIDetectionRequest):
    """
    Heuristic AI detection — no third-party API needed.

    Scores:
    - AI probability (0-100%)
    - Naturalness score (0-100, higher = more human)
    - Burstiness (sentence length variance)
    - Perplexity indicator (bigram diversity)
    - Specific AI phrase flags
    - Verdict: likely_ai | borderline | likely_human
    """
    try:
        result = analyze_ai_probability(req.content)
        return AIDetectionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI detection failed: {str(e)}")


@router.post("/snippet", response_model=SnippetOptimizationResponse)
async def optimize_snippet(req: SnippetOptimizationRequest):
    """
    Generate 3 featured snippet variants (paragraph, list, table)
    and score Google eligibility for each.

    Identifies the <!-- SNIPPET --> marked section or
    uses the best content paragraph automatically.
    """
    try:
        return await run_snippet_optimization(
            content=req.content,
            keyword=req.keyword,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Snippet optimization failed: {str(e)}")


@router.post("/links", response_model=InternalLinkResponse)
async def suggest_internal_links(req: InternalLinkRequest):
    """
    Analyze blog content against your existing blog catalog
    and suggest semantically relevant internal links with
    optimal anchor text placements.
    """
    try:
        return await run_internal_linking(
            content=req.content,
            existing_blogs=req.existing_blogs,
            primary_keyword=req.primary_keyword,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal linking failed: {str(e)}")
