from pydantic import BaseModel, Field
from typing import Optional, Any


# ── Keyword Clustering ────────────────────────────────────────────────────────
class KeywordCluster(BaseModel):
    cluster_name: str
    intent: str
    keywords: list[str]
    estimated_monthly_searches: str
    difficulty: str
    priority_score: float


class KeywordClusterResponse(BaseModel):
    seed_keyword: str
    clusters: list[KeywordCluster]
    total_keywords: int
    recommended_primary: str
    traffic_potential: str


# ── SERP Gap ──────────────────────────────────────────────────────────────────
class SERPResult(BaseModel):
    rank: int
    title: str
    url: str
    snippet: str
    word_count_estimate: int
    has_featured_snippet: bool
    content_type: str


class SERPGap(BaseModel):
    topic: str
    importance: str
    reason: str


# ✅ NEW: Content Gap Summary
class ContentGapSummary(BaseModel):
    title: str
    description: str


class SERPAnalysisResponse(BaseModel):
    keyword: str
    serp_personality: str
    results: list[SERPResult]
    content_gaps: list[SERPGap]

    # ✅ NEW FIELDS FOR YOUR UI
    missing_keywords: list[str] = []
    weak_sections: list[str] = []
    content_gap_summary: ContentGapSummary = ContentGapSummary(
        title="Untapped Opportunity",
        description="No major gap identified yet."
    )

    average_word_count: int
    recommended_format: str
    recommended_word_count: int
    winning_angle: str


# ── SEO Metrics ───────────────────────────────────────────────────────────────
class KeywordDensityDetail(BaseModel):
    keyword: str
    count: int
    density_percent: float
    status: str


class SEOScoreResponse(BaseModel):
    overall_score: float
    keyword_density: list[KeywordDensityDetail]
    readability_score: float
    readability_grade: str
    word_count: int
    heading_count: int
    has_meta_structure: bool
    internal_link_count: int
    keyword_in_title: bool
    keyword_in_first_100_words: bool
    lsi_keywords_found: list[str]
    issues: list[str]
    recommendations: list[str]
    projected_traffic_potential: str


# ── AI Detection ──────────────────────────────────────────────────────────────
class AIDetectionResponse(BaseModel):
    ai_probability_percent: float
    naturalness_score: float
    burstiness_score: float
    perplexity_indicator: str
    flags: list[str]
    verdict: str


# ── Snippet ───────────────────────────────────────────────────────────────────
class SnippetVariant(BaseModel):
    type: str
    content: str
    word_count: int
    snippet_score: float


class SnippetOptimizationResponse(BaseModel):
    keyword: str
    readiness_probability: float
    recommended_variant: SnippetVariant
    all_variants: list[SnippetVariant]
    optimization_tips: list[str]


# ── Internal Links ────────────────────────────────────────────────────────────
class InternalLinkSuggestion(BaseModel):
    anchor_text: str
    target_url: str
    target_title: str
    relevance_score: float
    placement_hint: str
    reason: str


class InternalLinkResponse(BaseModel):
    total_suggestions: int
    suggestions: list[InternalLinkSuggestion]
    linking_score: float


# ── Blog Generation ───────────────────────────────────────────────────────────
class HashNodePublishResult(BaseModel):
    success: bool
    hashnode_id: Optional[str] = None
    hashnode_url: Optional[str] = None
    message: str
    error: Optional[str] = None


class BlogGenerationResponse(BaseModel):
    title: str
    meta_description: str
    slug: str
    content: str
    word_count: int
    blog_id: Optional[str] = None

    # ✅ MAKE OPTIONAL (CRITICAL FIX)
    seo_score: Optional[SEOScoreResponse] = None
    ai_detection: Optional[AIDetectionResponse] = None
    snippet_optimization: Optional[SnippetOptimizationResponse] = None
    internal_links: Optional[InternalLinkResponse] = None

    keyword_clusters: Optional[KeywordClusterResponse] = None
    serp_analysis: Optional[SERPAnalysisResponse] = None

    generation_time_seconds: Optional[float] = None
    model_used: Optional[str] = None
    external_links_used: int = 0

    # 🔥 FIX WARNING
    model_config = {
        "protected_namespaces": ()
    }


class TitleSuggestionsResponse(BaseModel):
    titles: list[str] = Field(default_factory=list, description="SEO title suggestions")
