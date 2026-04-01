"""
Agent 5 — Snippet Optimization Agent
──────────────────────────────────────
Extracts the best snippet-ready section from the blog,
generates 3 format variants (paragraph, list, table),
and scores snippet readiness probability.
"""

import re

# Handle imports with fallback for different module contexts
try:
    from backend.services.groq_service import chat_completion_json
    from backend.utils.prompts import snippet_optimization_prompts
    from backend.models.response_models import SnippetVariant, SnippetOptimizationResponse
except ImportError:
    from ..services.groq_service import chat_completion_json
    from ..utils.prompts import snippet_optimization_prompts
    from ..models.response_models import SnippetVariant, SnippetOptimizationResponse


def _extract_snippet_section(content: str) -> str:
    """
    Look for the <!-- SNIPPET --> comment tag first.
    If not found, return the first 2000 chars of content.
    """
    match = re.search(r"<!--\s*SNIPPET\s*-->\s*(.+?)(?=\n#|\n\n|$)", content, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: first paragraph after H1
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and not p.startswith("#")]
    return paragraphs[0][:1000] if paragraphs else content[:1000]


def _score_variant(text: str, variant_type: str) -> float:
    """
    Score a snippet variant for Google eligibility.
    Paragraph: 40-60 words is ideal.
    List: 4-8 items is ideal.
    Table: presence of | chars.
    """
    word_count = len(text.split())
    score = 0.0

    if variant_type == "paragraph":
        if 35 <= word_count <= 65:
            score = 90.0
        elif 25 <= word_count < 35 or 65 < word_count <= 80:
            score = 70.0
        else:
            score = 50.0
    elif variant_type == "list":
        items = [l for l in text.split("\n") if l.strip().startswith(("1.", "2.", "-", "*"))]
        if 4 <= len(items) <= 8:
            score = 85.0
        elif len(items) > 0:
            score = 65.0
    elif variant_type == "table":
        if "|" in text and text.count("\n") >= 3:
            score = 75.0
        elif text:
            score = 40.0

    return round(score, 1)


async def run_snippet_optimization(
    content: str,
    keyword: str,
) -> SnippetOptimizationResponse:
    """
    Entry point for the Snippet Optimization Agent.
    """
    context = _extract_snippet_section(content)

    system, user = snippet_optimization_prompts(keyword, context)
    llm_data = await chat_completion_json(system, user, temperature=0.3)

    paragraph_text = llm_data.get("paragraph_variant", "")
    list_text = llm_data.get("list_variant", "")
    table_text = llm_data.get("table_variant") or ""

    # Ensure all variants are strings (LLM might return arrays instead of strings)
    paragraph_text = " ".join(paragraph_text) if isinstance(paragraph_text, list) else str(paragraph_text or "")
    list_text = " ".join(list_text) if isinstance(list_text, list) else str(list_text or "")
    table_text = " ".join(table_text) if isinstance(table_text, list) else str(table_text or "")

    paragraph_score = _score_variant(paragraph_text, "paragraph")
    list_score = _score_variant(list_text, "list")
    table_score = _score_variant(table_text, "table")

    variants = [
        SnippetVariant(type="paragraph", content=paragraph_text,
                       word_count=len(paragraph_text.split()), snippet_score=paragraph_score),
        SnippetVariant(type="list", content=list_text,
                       word_count=len(list_text.split()), snippet_score=list_score),
    ]
    if table_text:
        variants.append(
            SnippetVariant(type="table", content=table_text,
                           word_count=len(table_text.split()), snippet_score=table_score)
        )

    # Best variant by score
    best = max(variants, key=lambda v: v.snippet_score)

    readiness_probability = float(llm_data.get("readiness_probability", best.snippet_score))
    tips = llm_data.get("optimization_tips", [
        "Start with a direct definition sentence",
        "Keep paragraph answers between 40-60 words",
        "Use numbered lists for process-based queries",
    ])

    return SnippetOptimizationResponse(
        keyword=keyword,
        readiness_probability=round(readiness_probability, 1),
        recommended_variant=best,
        all_variants=variants,
        optimization_tips=tips,
    )
