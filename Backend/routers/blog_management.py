"""
Blog Management Router
======================
GET  /blog/list          — List saved blogs (sorted newest-first, paginated)
GET  /blog/{id}          — Get single blog by MongoDB ObjectId
PUT  /blog/{id}/status   — Update blog status (published/draft/archived)
PUT  /blog/{id}/publish-hashnode  — Publish blog to Hashnode
DELETE /blog/{id}        — Delete a blog
"""

import traceback

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from ..core.database import get_blogs_collection
from ..models.models import BlogResponse, BlogListResponse
from ..services.hashnode_service import publish_to_hashnode

router = APIRouter(prefix="/blog", tags=["Blog Management"])


# ── Response model ──────────────────────────────────────────────────────────
class BlogListItem(BaseModel):
    """Lightweight model for listing blogs"""
    id: str
    keyword: str
    title: str
    seo_score: int
    word_count: int
    status: str
    created_at: Optional[datetime] = None
    meta_description: Optional[str] = None
    slug: Optional[str] = None
    ai_detection_score: Optional[float] = None
    generation_time: Optional[float] = None


class BlogDetailResponse(BaseModel):
    """Full blog detail including content"""
    id: str
    keyword: str
    title: str
    content: str
    seo_score: int
    word_count: int
    target_word_count: Optional[int] = None
    status: str
    created_at: Optional[datetime] = None
    meta_description: Optional[str] = None
    slug: Optional[str] = None
    ai_detection_score: Optional[float] = None
    generation_time: Optional[float] = None


class StatusUpdateRequest(BaseModel):
    status: str  # published | draft | archived


class HashNodePublishRequest(BaseModel):
    tags: Optional[List[str]] = None  # Max 5 tags for Hashnode


# ── Helpers ─────────────────────────────────────────────────────────────────
def _is_valid_oid(id_str: str) -> bool:
    if not ObjectId:
        return False
    try:
        ObjectId(id_str)
        return True
    except Exception:
        return False


def _serialize_list_item(doc: dict) -> dict:
    """Normalize MongoDB document for API output."""
    item = dict(doc)

    # Convert ObjectId to string id
    if item.get("_id") is not None:
        item["id"] = str(item["_id"])
    item.pop("_id", None)

    # Ensure datetime fields are JSON-safe and optional
    if item.get("created_at") and not isinstance(item["created_at"], datetime):
        item["created_at"] = None
    if item.get("updated_at") and not isinstance(item["updated_at"], datetime):
        item["updated_at"] = None

    return item


@router.get("/list", response_model=List[BlogListResponse])
async def list_blogs(
    limit: int = Query(default=50, ge=1, le=200),
    skip: int = Query(default=0, ge=0),
    status: Optional[str] = Query(default=None),
):
    try:
        collection = get_blogs_collection()

        if collection is None:
            # Return empty result when DB is unavailable (non-blocking mode)
            return []

        query = {}
        if status:
            query["status"] = status

        cursor = (
            collection.find(query, {"content": 0})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        docs = await cursor.to_list(length=limit)

        results = []
        for d in docs:
            try:
                item = _serialize_list_item(d)
                item["seo_score"] = item.get("seo_score") or 0
                item["word_count"] = item.get("word_count") or 0
                item["status"] = item.get("status") or "published"

                results.append(BlogListResponse(**item))
            except Exception as inner_error:
                print("⚠️ Skipping invalid blog document:", inner_error)
                continue

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list blogs: {str(e)}")


@router.get("/list/count")
async def count_blogs(status: Optional[str] = Query(default=None)):
    """Count total blogs in the database (optionally filtered by status)"""
    try:
        collection = get_blogs_collection()

        if collection is None:
            return {"count": 0}

        query = {}
        if status:
            query["status"] = status

        count = await collection.count_documents(query)
        return {"count": count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to count blogs: {str(e)}")


@router.get("/{blog_id}", response_model=BlogResponse)
async def get_blog(blog_id: str):
    """Get a single blog by ID"""
    if not _is_valid_oid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID format")

    try:
        collection = get_blogs_collection()

        if collection is None:
            raise HTTPException(status_code=503, detail="Database unavailable")

        doc = await collection.find_one({"_id": ObjectId(blog_id)})

        if not doc:
            raise HTTPException(status_code=404, detail="Blog not found")

        item = _serialize_list_item(doc)
        item["seo_score"] = item.get("seo_score") or 0
        item["word_count"] = item.get("word_count") or 0
        item["status"] = item.get("status") or "published"

        return BlogResponse(**item)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get blog: {str(e)}")


@router.put("/{blog_id}/status")
async def update_blog_status(blog_id: str, req: StatusUpdateRequest):
    """Update blog status (published/draft/archived)"""
    if not _is_valid_oid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID format")

    valid_statuses = ["published", "draft", "archived"]
    if req.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    try:
        collection = get_blogs_collection()

        if collection is None:
            raise HTTPException(status_code=503, detail="Database unavailable")

        result = await collection.update_one(
            {"_id": ObjectId(blog_id)},
            {
                "$set": {
                    "status": req.status,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Blog not found")

        return {"status": "updated", "blog_id": blog_id, "new_status": req.status}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update blog status: {str(e)}")


@router.put("/{blog_id}/publish-hashnode")
async def publish_blog_to_hashnode(blog_id: str, req: HashNodePublishRequest):
    """
    Publish an existing blog to Hashnode.
    
    - If already published, returns current Hashnode URL
    - If not published, publishes and returns new Hashnode URL
    """
    if not _is_valid_oid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID format")
    
    try:
        collection = get_blogs_collection()
        doc = await collection.find_one({"_id": ObjectId(blog_id)})
        
        if not doc:
            raise HTTPException(status_code=404, detail="Blog not found")
        
        # Check if already published to Hashnode
        if doc.get("hashnode_published"):
            return {
                "status": "already_published",
                "message": "Blog is already published on Hashnode",
                "hashnode_url": doc.get("hashnode_url"),
                "hashnode_id": doc.get("hashnode_id"),
                "blog_id": blog_id,
            }
        
        # Publish to Hashnode
        meta = doc.get("metadata", {}) or {}
        hashnode_result = await publish_to_hashnode(
            title=doc.get("title", ""),
            content=doc.get("content", ""),
            slug=meta.get("slug", ""),
            meta_description=meta.get("meta_description", ""),
            tags=req.tags if req.tags else None,
            is_draft=False,
        )
        
        # Update MongoDB with Hashnode info if successful
        if hashnode_result.get("success"):
            await collection.update_one(
                {"_id": ObjectId(blog_id)},
                {
                    "$set": {
                        "hashnode_published": True,
                        "hashnode_id": hashnode_result.get("hashnode_id"),
                        "hashnode_url": hashnode_result.get("hashnode_url"),
                        "hashnode_published_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
            
            return {
                "status": "published",
                "message": "Blog successfully published to Hashnode",
                "hashnode_url": hashnode_result.get("hashnode_url"),
                "hashnode_id": hashnode_result.get("hashnode_id"),
                "blog_id": blog_id,
            }
        else:
            # Store error in MongoDB
            await collection.update_one(
                {"_id": ObjectId(blog_id)},
                {
                    "$set": {
                        "hashnode_error": hashnode_result.get("error"),
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
            
            raise HTTPException(
                status_code=500,
                detail=f"Failed to publish to Hashnode: {hashnode_result.get('error')}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish blog to Hashnode: {str(e)}")


@router.delete("/{blog_id}")
async def delete_blog(blog_id: str):
    """Permanently delete a blog by ID."""
    if not _is_valid_oid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID format")
    try:
        collection = get_blogs_collection()
        result = await collection.delete_one({"_id": ObjectId(blog_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Blog not found")
        return {"message": "Blog deleted successfully", "blog_id": blog_id}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to delete blog: {str(e)}")