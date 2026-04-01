# backend Restructuring Guide

## New Directory Structure

The backend has been reorganized into logical subfolders:

```
backend/
├── __init__.py              # Root package init
├── core/                    # Core configuration & database
│   ├── __init__.py
│   ├── config.py           # Environment variables & settings
│   ├── database.py         # MongoDB connection manager
│   └── main.py             # FastAPI app entry point
│
├── models/                  # Data models
│   ├── __init__.py
│   ├── models.py           # MongoDB document models
│   ├── request_models.py   # Request validation models
│   └── response_models.py  # Response models
│
├── services/               # External service integrations
│   ├── __init__.py
│   ├── groq_service.py     # LLM API wrapper (Groq)
│   ├── hashnode_service.py # Hashnode publishing API
│   └── ai_detection_service.py  # AI content detection
│
├── agents/                 # Content generation agents
│   ├── __init__.py
│   ├── keyword_agent.py    # Keyword clustering (Agent 1)
│   ├── serp_agent.py       # SERP analysis (Agent 2)
│   ├── blog_generator.py   # Blog generation (Agent 3)
│   ├── seo_optimizer.py    # SEO analysis (Agent 4)
│   ├── snippet_agent.py    # Snippet optimization (Agent 5)
│   ├── humanizer.py        # Content humanization (Agent 6)
│   └── internal_linking_agent.py  # Link suggestions (Agent 7)
│
├── routers/                # FastAPI route handlers
│   ├── __init__.py
│   ├── blog.py            # POST /blog/generate
│   ├── blog_management.py # Blog CRUD operations
│   ├── keywords.py        # Keyword operations
│   ├── serp.py            # SERP analysis endpoint
│   └── seo.py             # SEO analysis endpoints
│
├── utils/                  # Utility functions & helpers
│   ├── __init__.py
│   ├── prompts.py         # LLM prompt templates
│   ├── seo_utils.py       # SEO calculation utilities
│   └── scraper.py         # Web scraping utilities
│
├── debug/                  # Testing & debugging tools
│   ├── __init__.py
│   ├── debug_hashnode.py   # Hashnode API testing
│   ├── test_hashnode.py    # Hashnode integration tests
│   ├── test_mongodb.py     # MongoDB tests
│   ├── test_api.py         # API endpoint tests
│   ├── hashnode_examples.py # Example code
│   └── check_mongo_full.py # MongoDB inspection
│
├── requirements.txt        # Python dependencies
├── render.yaml            # Deployment config
├── .env                   # Environment variables (DO NOT COMMIT)
├── .env.example           # Example environment file
└── .gitignore             # Git ignore rules
```

## Running the Application

### Starting the backend Server

The server entry point has moved to `core/main.py`. Use:

```bash
cd backend
uvicorn core.main:app --reload --host 0.0.0.0 --port 8000
```

Or if running from the parent directory:

```bash
uvicorn backend.core.main:app --reload --host 0.0.0.0 --port 8000
```

### Import Structure

All imports within the backend now use relative imports:

- Routers import from: `..models`, `..services`, `..agents`, `..utils`, `..core`
- Agents import from: `..services`, `..utils`, `..models`, `..core`
- Services import from: `..core`
- Utils import from: `..core`

Example:
```python
# In routers/blog.py
from ..models.request_models import BlogGenerationRequest
from ..services.groq_service import chat_completion_json
from ..agents.keyword_agent import run_keyword_clustering
```

## Benefits of This Structure

✅ **Separation of Concerns** - Each module has a clear responsibility
✅ **Scalability** - Easy to add new agents, services, or routes
✅ **Maintainability** - Logical organization makes code easier to find and modify
✅ **Testing** - Clear boundaries make unit testing simpler
✅ **Onboarding** - New developers can quickly understand the architecture

## Frontend Changes

No changes needed! The frontend continues to call the same API endpoints:
- `/blog/generate`
- `/blog/list`
- `/keywords/cluster`
- `/serp/analyze`
- `/seo/analyze`
- etc.

The internal restructuring is transparent to the frontend.

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`, ensure:
1. You're running from the `backend` directory
2. PYTHONPATH includes the backend directory
3. All relative imports use `..` correctly

### Database Connection

Database configuration is in `core/config.py`. Ensure `.env` has:
```
MONGODB_URL=your_mongodb_connection_string
MONGODB_DB_NAME=your_db_name
```

### Debug/Test Scripts

To run debug scripts from the backend directory:
```bash
python -m debug.debug_hashnode
python -m debug.test_hashnode
```
