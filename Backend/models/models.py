"""
Data Models
===========
Pydantic models for MongoDB documents
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any
from bson import ObjectId


class BlogDocument(BaseModel):
    """MongoDB Blog Document Schema"""
    id: Optional[str] = Field(alias="_id", default=None)
    keyword: str
    target_word_count: int
    content: str
    title: str
    seo_score: int
    word_count: int
    metadata: dict = Field(default_factory=dict)  # Stores full response data
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None  # For multi-user support later
    status: str = "published"  # published, draft, archived
    
    # ── Hashnode Publishing ──────────────────────────────────────────────────
    hashnode_published: bool = False
    hashnode_id: Optional[str] = None
    hashnode_url: Optional[str] = None
    hashnode_published_at: Optional[datetime] = None
    hashnode_error: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "keyword": "AI in 2024",
                "target_word_count": 2500,
                "content": "# AI in 2024\n\n...",
                "title": "AI in 2024",
                "seo_score": 82,
                "word_count": 2576,
                "status": "published"
            }
        }


class BlogResponse(BaseModel):
    """Response model for blog API"""
    id: Optional[str] = None
    keyword: str
    content: str
    title: str
    seo_score: int
    word_count: int
    created_at: Optional[datetime] = None
    status: str = "published"
    generation_time: Optional[float] = None
    meta_description: Optional[str] = None
    slug: Optional[str] = None
    ai_detection_score: Optional[float] = None


class BlogListResponse(BaseModel):
    """Lightweight response model for blog list endpoint (no content)"""
    id: Optional[str] = None
    keyword: str
    title: str
    seo_score: int
    word_count: int
    created_at: Optional[datetime] = None
    status: str = "published"
    meta_description: Optional[str] = None
    slug: Optional[str] = None
    generation_time: Optional[float] = None
    ai_detection_score: Optional[float] = None


class UserDocument(BaseModel):
    """MongoDB User Document Schema (for future multi-user support)"""
    id: Optional[str] = Field(alias="_id", default=None)
    email: str
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    blog_count: int = 0

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
