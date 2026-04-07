"""
POST /blog/generate — Full pipeline endpoint.
Orchestrates: Web Search → SERP → Keywords → Generate → SEO → Snippet → Humanize → Internal Links → Hashnode (optional)
"""

import time
import asyncio
from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId

# Handle imports with fallback for different module contexts
try:
    # When run as: uvicorn Backend.core.main:app
    from Backend.models.request_models import BlogGenerationRequest
    from Backend.models.response_models import BlogGenerationResponse, AIDetectionResponse, HashNodePublishResult
    from Backend.agents.keyword_agent import run_keyword_clustering
    from Backend.agents.serp_agent import run_serp_analysis
    from Backend.agents.web_search_agent import run_web_search, format_web_search_context
    from Backend.agents.blog_generator import run_blog_generation
    from Backend.agents.seo_optimizer import run_seo_analysis
    from Backend.agents.snippet_agent import run_snippet_optimization
    from Backend.agents.humanizer import run_humanization
    from Backend.agents.internal_linking_agent import run_internal_linking
    from Backend.services.ai_detection_service import analyze_ai_probability
    from Backend.core.config import GROQ_MODEL, HASHNODE_AUTO_PUBLISH
    from Backend.services.hashnode_service import publish_to_hashnode
    from Backend.core.database import get_blogs_collection
    from Backend.models.models import BlogDocument
except ImportError:
    # Fallback for relative imports
    from ..models.request_models import BlogGenerationRequest
    from ..models.response_models import BlogGenerationResponse, AIDetectionResponse, HashNodePublishResult
    from ..agents.keyword_agent import run_keyword_clustering
    from ..agents.serp_agent import run_serp_analysis
    from ..agents.web_search_agent import run_web_search, format_web_search_context
    from ..agents.blog_generator import run_blog_generation
    from ..agents.seo_optimizer import run_seo_analysis
    from ..agents.snippet_agent import run_snippet_optimization
    from ..agents.humanizer import run_humanization
    from ..agents.internal_linking_agent import run_internal_linking
    from ..services.ai_detection_service import analyze_ai_probability
    from ..core.config import GROQ_MODEL, HASHNODE_AUTO_PUBLISH
    from ..services.hashnode_service import publish_to_hashnode
    from ..core.database import get_blogs_collection
    from ..models.models import BlogDocument

router = APIRouter(prefix="/blog", tags=["Blog Generation"])


@router.post("/generate", response_model=BlogGenerationResponse)
async def generate_blog(req: BlogGenerationRequest):
    """
    Full blog generation pipeline. All agents run in optimized order.

    Pipeline:
    0. Web Search              (Latest information from internet)
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
        # ── Step 0: Web Search (Optional - Latest Information) ──────────────
        web_search_data = None
        if req.enable_web_search:
            try:
                print(f"🔍 Fetching latest web information for: {req.keyword}")
                web_search_data = await run_web_search(
                    keyword=req.keyword,
                    max_results=8,
                    extract_insights=True,
                )
                print(f"✓ Web search completed: {web_search_data['results_count']} sources found")
            except Exception as e:
                print(f"⚠️  Web search failed: {e}")
                web_search_data = None
        
        # ── Step 1: Keyword Clustering (Groq LLM) ─────────────────────────────
        keyword_clusters = None
        if req.enable_serp_analysis:
            try:
                keyword_clusters = await run_keyword_clustering(
                    seed_keyword=req.keyword,
                    target_location=req.target_location,
                    cluster_count=5,
                )
            except Exception as e:
                print(f"⚠️  Keyword clustering failed: {e}")
                keyword_clusters = None

        # ── Step 2: SERP Analysis (DuckDuckGo scrape + Groq LLM) ──────────────
        serp_analysis = None
        if req.enable_serp_analysis and req.serp_analysis is None:
            try:
                serp_analysis = await run_serp_analysis(
                    keyword=req.keyword,
                    target_location=req.target_location,
                    competitor_urls=req.competitor_urls,
                )
            except Exception as e:
                print(f"⚠️  SERP analysis failed: {e}")
                serp_analysis = None
        elif req.serp_analysis is not None:
            serp_analysis = req.serp_analysis

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
            web_search_data=web_search_data,
        )

        content = blog_data["content"]
        title = blog_data["title"]

        # ── Step 4: AI Detection ───────────────────────────────────────────────
        ai_detection_dict = analyze_ai_probability(content)

        # ── Step 5: Humanization (if enabled) ─────────────────────────────────
        if req.enable_humanization:
            content, ai_detection_dict = await run_humanization(content, ai_detection_dict)

        ai_detection = AIDetectionResponse(**ai_detection_dict)

        # ── Step 6: SEO Analysis ──────────────────────────────────────────────
        seo_score = await run_seo_analysis(
            content=content,
            title=title,
            keyword=req.keyword,
            secondary_keywords=req.secondary_keywords,
        )

        # ── Step 7: Snippet Optimization ──────────────────────────────────────
        snippet_optimization = await run_snippet_optimization(
            content=content, keyword=req.keyword
        )

        # ── Step 8: Internal Linking ──────────────────────────────────────────
        if req.internal_links:
            internal_links = await run_internal_linking(
                content=content,
                existing_blogs=req.internal_links,
                primary_keyword=req.keyword,
            )
        else:
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

        collection = get_blogs_collection()
        if collection is None:
            raise HTTPException(
                status_code=503,
                detail="MongoDB is unavailable. Cannot save generated blog."
            )

        try:
            result = await collection.insert_one(blog_doc.dict())
            blog_id = str(result.inserted_id)
        except Exception as db_error:
            print(f"⚠️  MongoDB save failed: {db_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save generated blog to MongoDB: {db_error}"
            )

        # ── Publish to Hashnode (if enabled) ──────────────────────────────────
        hashnode_result = None
        should_publish_hashnode = req.publish_to_hashnode or HASHNODE_AUTO_PUBLISH
        
        if should_publish_hashnode:
            try:
                slug = blog_data.get("slug", "")
                hashnode_publish_result = await publish_to_hashnode(
                    title=title,
                    content=content,
                    slug=slug,
                    meta_description=blog_data.get("meta_description", ""),
                    tags=req.hashnode_tags if req.hashnode_tags else None,
                    is_draft=False,
                )
                
                hashnode_result = HashNodePublishResult(**hashnode_publish_result)
                
                # Update MongoDB document with Hashnode info if publish was successful
                if hashnode_publish_result.get("success") and blog_id:
                    try:
                        await collection.update_one(
                            {"_id": ObjectId(blog_id)},
                            {
                                "$set": {
                                    "hashnode_published": True,
                                    "hashnode_id": hashnode_publish_result.get("hashnode_id"),
                                    "hashnode_url": hashnode_publish_result.get("hashnode_url"),
                                    "hashnode_published_at": datetime.utcnow(),
                                }
                            }
                        )
                    except Exception as update_error:
                        print(f"⚠️  Failed to update MongoDB with Hashnode data: {update_error}")
                elif hashnode_publish_result.get("error") and blog_id:
                    try:
                        await collection.update_one(
                            {"_id": ObjectId(blog_id)},
                            {
                                "$set": {
                                    "hashnode_error": hashnode_publish_result.get("error"),
                                }
                            }
                        )
                    except Exception as update_error:
                        print(f"⚠️  Failed to update MongoDB with Hashnode error: {update_error}")
                        
            except Exception as hashnode_error:
                print(f"⚠️  Hashnode publishing failed (non-blocking): {hashnode_error}")
                hashnode_result = HashNodePublishResult(
                    success=False,
                    message="Failed to publish to Hashnode",
                    error=str(hashnode_error)
                )

        response = BlogGenerationResponse(
            title=title,
            meta_description=blog_data["meta_description"],
            slug=blog_data["slug"],
            content=content,
            word_count=blog_data.get("word_count", seo_word_count),
            blog_id=blog_id,
            external_links_used=len(req.competitor_urls) if req.competitor_urls else 0,
            seo_score=seo_score,
            ai_detection=ai_detection,
            snippet_optimization=snippet_optimization,
            internal_links=internal_links,
            keyword_clusters=keyword_clusters,
            serp_analysis=serp_analysis,
            generation_time_seconds=elapsed,
            model_used=GROQ_MODEL,
        )

        # Add blog_id to response if saved successfully
        if blog_id:
            response.blog_id = blog_id

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blog generation failed: {str(e)}")