"""
POST /blog/generate — Full pipeline endpoint.
Orchestrates: SERP → Keywords → Generate → SEO → Snippet → Humanize → Internal Links
"""

import time
import asyncio
from fastapi import APIRouter, HTTPException
from request_models import BlogGenerationRequest
from models.response_models import (
    BlogGenerationResponse, 
    AIDetectionResponse,
    SEOScoreResponse,
    SnippetOptimizationResponse,
    InternalLinkResponse,
    SnippetVariant
)

from keyword_agent import run_keyword_clustering
from serp_agent import run_serp_analysis
from blog_generator import run_blog_generation
from seo_optimizer import run_seo_analysis
from snippet_agent import run_snippet_optimization
from humanizer import run_humanization
from internal_linking_agent import run_internal_linking
from ai_detection_service import analyze_ai_probability
from config import GROQ_MODEL

# ── Database ────────────────────────────────────────────────────────────────
from backend.core.database import get_blogs_collection
from models import BlogDocument
from datetime import datetime

router = APIRouter(prefix="/blog", tags=["Blog Generation"])


@router.post("/generate", response_model=BlogGenerationResponse)
async def generate_blog(req: BlogGenerationRequest):
    """
    Full blog generation pipeline. All agents run in optimized order.

    Pipeline:
    1. Keyword Clustering      (Groq LLM)
    2. SERP Gap Analysis       (DuckDuckGo scrape + Groq LLM)
    3. Blog Generation         (Groq LLM — main content)
    4. AI Detection            (Heuristic)
    5. Humanization            (Groq LLM — if needed)
    6. SEO Analysis            (Deterministic)
    7. Snippet Optimization    (Groq LLM)
    8. Internal Linking        (Groq LLM — if links provided)
    """
    start_time = time.time()

    try:
        # ── Step 1+2 in parallel: Keyword Clustering + SERP Analysis ──────────
        keyword_task = run_keyword_clustering(
            seed_keyword=req.keyword,
            target_location=req.target_location,
            cluster_count=5,
        )
        serp_task = run_serp_analysis(
            keyword=req.keyword,
            target_location=req.target_location,
            competitor_urls=req.competitor_urls,
        )

        keyword_clusters, serp_analysis = await asyncio.gather(
            keyword_task, serp_task, return_exceptions=True
        )

        # Graceful degradation if either fails
        if isinstance(keyword_clusters, Exception):
            keyword_clusters = None
        if isinstance(serp_analysis, Exception):
            serp_analysis = None

        # ── Step 3: Blog Generation ────────────────────────────────────────────
        blog_data = await run_blog_generation(
            keyword=req.keyword,
            secondary_keywords=req.secondary_keywords,
            target_location=req.target_location,
            word_count=req.word_count,
            tone=req.tone,
            serp_analysis=serp_analysis,
            keyword_clusters=keyword_clusters,
            internal_links=req.internal_links,
            title_override=req.blog_title,
            competitor_urls=req.competitor_urls,
        )

        content = blog_data["content"]
        title = blog_data["title"]

        # ── Step 4: AI Detection ───────────────────────────────────────────────
        ai_detection_dict = analyze_ai_probability(content)

        # ── Step 5: Humanization (if enabled) ─────────────────────────────────
        if req.enable_humanization:
            content, ai_detection_dict = await run_humanization(content, ai_detection_dict)

        ai_detection = AIDetectionResponse(**ai_detection_dict)

        # ── Step 6+7+8 in parallel: SEO + Snippet + Internal Links ────────────
        seo_task = run_seo_analysis(
            content=content,
            title=title,
            keyword=req.keyword,
            secondary_keywords=req.secondary_keywords,
        )
        snippet_task = run_snippet_optimization(content=content, keyword=req.keyword)
        link_task = run_internal_linking(
            content=content,
            existing_blogs=req.internal_links,
            primary_keyword=req.keyword,
        )

        seo_score, snippet_optimization, internal_links = await asyncio.gather(
            seo_task, snippet_task, link_task, return_exceptions=True
        )

        # Graceful degradation if any analysis fails
        if isinstance(seo_score, Exception):
            seo_score = None
        if isinstance(snippet_optimization, Exception):
            snippet_optimization = None
        if isinstance(internal_links, Exception):
            internal_links = None

        elapsed = round(time.time() - start_time, 2)

        # ── Extract values safely ─────────────────────────────────────────────
        seo_overall_score = 0
        seo_word_count = 0
        ai_detection_score = 0
        
        if hasattr(seo_score, 'overall_score'):
            seo_overall_score = seo_score.overall_score
        if hasattr(seo_score, 'word_count'):
            seo_word_count = seo_score.word_count
        if hasattr(ai_detection, 'ai_probability_percent'):
            ai_detection_score = ai_detection.ai_probability_percent / 100.0  # Convert to 0-1 range

        # ── Save to MongoDB ───────────────────────────────────────────────────
        try:
            blogs_collection = get_blogs_collection()
            if not blogs_collection:
                raise HTTPException(
                    status_code=503,
                    detail="MongoDB unavailable. Please check MONGODB_URL and ensure the database is running."
                )

            blog_doc = BlogDocument(
                keyword=req.keyword,
                target_word_count=req.word_count,
                content=content,
                title=title,
                seo_score=int(seo_overall_score),
                word_count=blog_data.get("word_count", seo_word_count),
                metadata={
                    "meta_description": blog_data.get("meta_description", ""),
                    "slug": blog_data.get("slug", ""),
                    "ai_detection_score": ai_detection_score,
                    "generation_time": elapsed,
                },
                status="published"
            )
            
            result = await blogs_collection.insert_one(blog_doc.model_dump(by_alias=True, exclude_none=True))
            blog_id = str(result.inserted_id)
        except HTTPException:
            raise
        except Exception as db_error:
            print(f"⚠️  MongoDB save failed: {db_error}")
            raise HTTPException(status_code=500, detail=f"MongoDB save failed: {db_error}")

        response = BlogGenerationResponse(
            title=title,
            meta_description=blog_data["meta_description"],
            slug=blog_data["slug"],
            content=content,
            word_count=blog_data.get("word_count", seo_word_count),
            seo_score=seo_score,
            ai_detection=ai_detection,
            snippet_optimization=snippet_optimization,
            internal_links=internal_links,
            keyword_clusters=keyword_clusters if not isinstance(keyword_clusters, Exception) else None,
            serp_analysis=serp_analysis if not isinstance(serp_analysis, Exception) else None,
            generation_time_seconds=elapsed,
            model_used=GROQ_MODEL,
            external_links_used=len(req.competitor_urls),
        )
        
        # Add blog_id to response if saved successfully
        if blog_id:
            response.blog_id = blog_id

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blog generation failed: {str(e)}")
