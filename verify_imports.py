#!/usr/bin/env python3
"""
Import verification script for the backend restructuring
Run this to validate all imports are correct
"""

import sys
sys.path.insert(0, '.')

print("🔍 Verifying backend imports...")

try:
    print("  ✓ Importing core modules...")
    from Backend.core.config import APP_HOST, APP_PORT
    from Backend.core.database import get_blogs_collection
    
    print("  ✓ Importing models...")
    from Backend.models.models import BlogDocument
    from Backend.models.request_models import BlogGenerationRequest
    from Backend.models.response_models import BlogGenerationResponse
    
    print("  ✓ Importing services...")
    from Backend.services.groq_service import chat_completion
    from Backend.services.hashnode_service import publish_to_hashnode
    from Backend.services.ai_detection_service import analyze_ai_probability
    
    print("  ✓ Importing agents...")
    from Backend.agents.keyword_agent import run_keyword_clustering
    from Backend.agents.serp_agent import run_serp_analysis
    from Backend.agents.blog_generator import run_blog_generation
    from Backend.agents.seo_optimizer import run_seo_analysis
    from Backend.agents.snippet_agent import run_snippet_optimization
    from Backend.agents.humanizer import run_humanization
    from Backend.agents.internal_linking_agent import run_internal_linking
    
    print("  ✓ Importing routers...")
    from Backend.routers.blog import router as blog_router
    from Backend.routers.blog_management import router as blog_management_router
    from Backend.routers.keywords import router as keywords_router
    from Backend.routers.serp import router as serp_router
    from Backend.routers.seo import router as seo_router
    
    print("  ✓ Importing main app...")
    from Backend.core.main import app
    
    print("\n✅ All imports successful!")
    print("\n✨ backend structure is valid and ready to run!")
    print("\nTo start the server, run:")
    print("  python -m uvicorn backend.core.main:app --reload --host 0.0.0.0 --port 8000")
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
