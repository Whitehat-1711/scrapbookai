"""
Blogy AI Blog Engine — FastAPI Application
==========================================
All routers registered here. Run with one of:

  Option 1 (from Backend directory):
    python -m uvicorn Backend.core.main:app --reload --host 0.0.0.0 --port 8000

  Option 2 (from Backend directory with PYTHONPATH):
    set PYTHONPATH=%cd% && uvicorn core.main:app --reload --host 0.0.0.0 --port 8000
"""

import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import APP_HOST, APP_PORT, CORS_ORIGINS, GROQ_MODEL, APP_ENV
from .database import connect_to_mongo, disconnect_from_mongo

# Import routers - choose import style by module package context.
# `core.main`   (Render rootDir=Backend) -> import from `routers.*`
# `Backend.core.main` (repo root)        -> import from `Backend.routers.*`
_ROOT_PACKAGE = (__package__ or "").split(".")[0]

if _ROOT_PACKAGE == "Backend":
    from Backend.routers.blog import router as blog_router
    from Backend.routers.blog_management import router as blog_management_router
    from Backend.routers.keywords import router as keywords_router
    from Backend.routers.serp import router as serp_router
    from Backend.routers.seo import router as seo_router
    from Backend.routers.humanize import router as humanize_router
    from Backend.routers.auth import router as auth_router
else:
    from routers.blog import router as blog_router
    from routers.blog_management import router as blog_management_router
    from routers.keywords import router as keywords_router
    from routers.serp import router as serp_router
    from routers.seo import router as seo_router
    from routers.humanize import router as humanize_router
    from routers.auth import router as auth_router

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("blogy")


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Blogy AI Engine starting up...")
    logger.info(f"   Model  : {GROQ_MODEL}")
    logger.info(f"   Env    : {APP_ENV}")
    logger.info(f"   Host   : {APP_HOST}:{APP_PORT}")
    
    # Connect to MongoDB
    try:
        await connect_to_mongo()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # Don't raise - allow app to start for API-only mode
    
    yield
    
    # Disconnect from MongoDB
    await disconnect_from_mongo()
    logger.info("🛑 Blogy AI Engine shutting down...")


# ── App Factory ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Blogy AI Blog Engine",
    description="""
## 🚀 AI-Powered SEO Blog Generation Engine

Built with **Groq (llama-3.3-70b-versatile)** for blazing-fast generation.

### Pipeline
1. **Keyword Clustering** — Intent-grouped clusters with traffic estimates
2. **SERP Gap Analysis** — Competitor scraping + content gap identification  
3. **Blog Generation** — Full SEO-optimized blog via structured prompts
4. **AI Detection** — Heuristic scoring (burstiness, perplexity, AI phrases)
5. **Humanization** — Automatic rewrite if AI score is high
6. **SEO Scoring** — Keyword density, readability, heading structure, LSI
7. **Snippet Optimization** — 3-variant featured snippet engineering
8. **Internal Linking** — Semantic link suggestions from your blog catalog

### Metrics Tracked
- Prompt Architecture Clarity
- Keyword Clustering Logic
- SERP Gap Identification
- Projected Traffic Potential
- SEO Optimization Percentage
- AI Detection % & Naturalness Score
- Snippet Readiness Probability
- Keyword Density Compliance
- Internal Linking Logic
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Timing Middleware ──────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = round(time.time() - start, 3)
    response.headers["X-Process-Time"] = f"{elapsed}s"
    logger.info(f"{request.method} {request.url.path} → {response.status_code} [{elapsed}s]")
    return response


# ── Global Exception Handler ───────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


# ── Register Routers ───────────────────────────────────────────────────────────
app.include_router(blog_router)
app.include_router(blog_management_router)
app.include_router(keywords_router)
app.include_router(serp_router)
app.include_router(seo_router)
app.include_router(humanize_router)
app.include_router(auth_router)


# ── Root & Health ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "name": "Blogy AI Blog Engine",
        "version": "1.0.0",
        "status": "running",
        "model": GROQ_MODEL,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "model": GROQ_MODEL,
        "environment": APP_ENV,
    }


# ── Dev Runner ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "core.main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=(APP_ENV == "development"),
        log_level="info",
    )

