from pydantic import BaseModel, Field
from typing import Optional

from .response_models import SERPAnalysisResponse


class BlogGenerationRequest(BaseModel):
    keyword: str = Field(..., min_length=2, description="Primary target keyword")
    secondary_keywords: list[str] = Field(default=[], description="Supporting keywords")
    target_location: str = Field(default="India", description="GEO target (city/country)")
    serp_analysis: Optional[SERPAnalysisResponse] = Field(default=None, description="Optional SERP intelligence from prior analysis")
    blog_title: Optional[str] = Field(default=None, description="Override auto title")
    word_count: int = Field(default=2500, ge=800, le=5000)
    tone: str = Field(default="professional", description="professional|conversational|authoritative")
    competitor_urls: list[str] = Field(default=[], max_length=5)
    internal_links: list[dict] = Field(
        default=[],
        description="[{'title': 'Blog Title', 'url': 'https://...', 'topic': 'topic'}]"
    )
    enable_humanization: bool = Field(default=True)
    publish_to_hashnode: bool = Field(default=False, description="Publish to Hashnode after generation")
    hashnode_tags: list[str] = Field(default=[], description="Tags for Hashnode (max 5)", max_length=5)


class KeywordClusterRequest(BaseModel):
    seed_keyword: str = Field(..., min_length=2)
    target_location: str = Field(default="India")
    cluster_count: int = Field(default=5, ge=2, le=10)


class SERPAnalysisRequest(BaseModel):
    keyword: str = Field(..., min_length=2)
    target_location: str = Field(default="India")
    max_results: int = Field(default=10, ge=3, le=10)
    competitor_urls: list[str] = Field(default=[], max_length=5)


class SEOAnalysisRequest(BaseModel):
    content: str = Field(..., min_length=100)
    keyword: str = Field(..., min_length=2)
    secondary_keywords: list[str] = Field(default=[])


class SnippetOptimizationRequest(BaseModel):
    content: str = Field(..., min_length=100)
    keyword: str = Field(..., min_length=2)


class AIDetectionRequest(BaseModel):
    content: str = Field(..., min_length=100)


class InternalLinkRequest(BaseModel):
    content: str = Field(..., min_length=100)
    existing_blogs: list[dict] = Field(
        ...,
        description="[{'title': str, 'url': str, 'topic': str, 'keywords': [str]}]"
    )
    primary_keyword: str
