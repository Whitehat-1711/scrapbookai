"""
Agent 1 — Keyword Clustering Agent
────────────────────────────────────
Uses Groq LLM to cluster a seed keyword into intent-grouped clusters
with estimated traffic and difficulty.
"""

# Handle imports with fallback for different module contexts
try:
    from Backend.services.groq_service import chat_completion_json
    from Backend.utils.prompts import keyword_cluster_prompts
    from Backend.models.response_models import KeywordCluster, KeywordClusterResponse
except ImportError:
    from ..services.groq_service import chat_completion_json
    from ..utils.prompts import keyword_cluster_prompts
    from ..models.response_models import KeywordCluster, KeywordClusterResponse


async def run_keyword_clustering(
    seed_keyword: str,
    target_location: str = "India",
    cluster_count: int = 5,
) -> KeywordClusterResponse:
    """
    Entry point for the Keyword Clustering Agent.
    Returns a KeywordClusterResponse with clusters and metadata.
    """
    system, user = keyword_cluster_prompts(seed_keyword, target_location, cluster_count)
    data = await chat_completion_json(system, user, temperature=0.4)

    clusters = [
        KeywordCluster(
            cluster_name=c.get("cluster_name", ""),
            intent=c.get("intent", "informational"),
            keywords=c.get("keywords", []),
            estimated_monthly_searches=c.get("estimated_monthly_searches", "N/A"),
            difficulty=c.get("difficulty", "medium"),
            priority_score=float(c.get("priority_score", 5.0)),
        )
        for c in data.get("clusters", [])
    ]

    return KeywordClusterResponse(
        seed_keyword=seed_keyword,
        clusters=clusters,
        total_keywords=sum(len(c.keywords) for c in clusters),
        recommended_primary=data.get("recommended_primary", seed_keyword),
        traffic_potential=data.get("traffic_potential", "Unknown"),
    )
