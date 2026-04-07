"""
Prompt templates for all agents.
Each prompt is a (system, user) tuple factory function.
"""

from __future__ import annotations

# ══════════════════════════════════════════════════════════════════════════════
# KEYWORD CLUSTERING PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

def keyword_cluster_prompts(seed_keyword: str, location: str, cluster_count: int) -> tuple[str, str]:
    system = """You are a senior SEO strategist specializing in keyword research.
You cluster keywords by search intent and estimate realistic traffic potential.
You MUST return valid, well-formatted JSON only — no markdown, no explanation."""

    user = f"""Analyze the seed keyword: "{seed_keyword}" for the target location: "{location}".

Generate exactly {cluster_count} keyword clusters. For each cluster, provide:
- cluster_name: short descriptive name (string)
- intent: one of [informational, transactional, navigational, commercial] (string)
- keywords: list of 4-6 related keywords (array of strings)
- estimated_monthly_searches: realistic range string e.g. "1,000-5,000" (string)
- difficulty: one of [low, medium, high] (string)
- priority_score: priority score 0-10 (number)

Also provide:
- recommended_primary: the single best keyword to target first (string)
- traffic_potential: overall traffic opportunity description (string)

Return ONLY valid JSON with this exact structure:
{{
  "seed_keyword": "{seed_keyword}",
  "clusters": [
    {{
      "cluster_name": "Example Cluster",
      "intent": "informational",
      "keywords": ["keyword1", "keyword2", "keyword3"],
      "estimated_monthly_searches": "5,000-10,000",
      "difficulty": "medium",
      "priority_score": 7.5
    }}
  ],
  "total_keywords": <total count as number>,
  "recommended_primary": "{seed_keyword}",
  "traffic_potential": "High opportunity with moderate competition"
}}"""
    return system, user


# ══════════════════════════════════════════════════════════════════════════════
# SERP GAP ANALYSIS PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

def serp_gap_prompts(keyword: str, serp_data: list[dict], page_data: list[dict], competitor_summary: str, coverage_map: dict) -> tuple[str, str]:
    system = """You are an expert content strategist and SERP analyst.
Given the top search results for a keyword, competitor content analysis, and coverage maps, identify:
1. The dominant SERP personality (listicle, long-form, guide, etc.)
2. Content gaps that top results ALL missed
3. The best angle to outrank them
4. Missing keywords not well covered by competitors
5. Weak sections competitors are shallow on
6. A specific content gap summary
Return valid JSON only."""

    serp_summary = "\n".join(
        [f"Rank {i+1}: {r['title']} — {r['snippet'][:150]}" for i, r in enumerate(serp_data[:8])]
    )

    # Summarize page data
    page_summary = "\n---\n".join([
        f"Page {i+1}: {data.get('text', '')[:300]}... | Headings: {', '.join([h['text'] for h in data.get('headings', [])[:3]])} | Keywords: {', '.join([str(k) for k in data.get('keywords', [])[:5]])}"
        for i, data in enumerate(page_data[:5]) if data.get('text')
    ])

    user = f"""Keyword: "{keyword}"

TOP SERP RESULTS:
{serp_summary}

COMPETITOR CONTENT ANALYSIS:
{competitor_summary}

DETAILED COMPETITOR DATA:
{page_summary}

COMPETITOR COVERAGE MAP:
Headings: {', '.join([str(h) for h in coverage_map.get('headings', [])[:10]])}
Keywords: {', '.join([str(k) for k in coverage_map.get('keywords', [])[:15]])}
Topics: {', '.join([str(t) for t in coverage_map.get('topics', [])[:10]])}

Analyze and return this exact JSON:
{{
  "serp_personality": "<dominant format>",
  "content_gaps": [
    {{"topic": "<gap>", "importance": "high|medium|low", "reason": "<why it matters>"}}
  ],
  "missing_keywords": ["<keyword1>", "<keyword2>", "<keyword3>", "<keyword4>", "<keyword5>"],
  "weak_sections": ["<section1>", "<section2>", "<section3>"],
  "content_gap_summary": {{
    "title": "<specific gap title>",
    "description": "<detailed description of the gap>"
  }},
  "recommended_format": "<best format to use>",
  "recommended_word_count": <int>,
  "winning_angle": "<unique angle to outrank all competitors>"
}}

REQUIREMENTS:
- missing_keywords: At least 3-5 important keywords NOT well covered by competitors. Extract from competitor content analysis and coverage map.
- weak_sections: 2-4 sections competitors are shallow on (e.g., "Implementation Challenges", "Cost Analysis").
- content_gap_summary: Make it specific, not generic. Title should be actionable.
- If LLM can't find gaps, use heuristic extraction from competitor texts and coverage map."""
    return system, user
    return system, user


# ══════════════════════════════════════════════════════════════════════════════
# BLOG GENERATION PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

"""
Blog Generation Prompts — Improved
Supports any topic, region, blog type, and audience.
"""

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

_BLOG_TYPE_GUIDES: dict[str, str] = {
    "tutorial": (
        "Step-by-step structure. Start with prerequisites, then numbered steps, "
        "include working code snippets where relevant, end with a troubleshooting FAQ."
    ),
    "listicle": (
        "Lead with a promise ('X ways to…'). Each item gets its own H3, "
        "a 2-3 sentence explanation, and a concrete example. No filler padding."
    ),
    "comparison": (
        "Open with the decision context. Use a comparison table early. "
        "Dedicated H2 per option with pros/cons. End with a clear recommendation based on use case."
    ),
    "opinion_editorial": (
        "Strong POV in the first paragraph. Anticipate and address counter-arguments. "
        "Use data and examples to back claims. Personal voice throughout."
    ),
    "explainer": (
        "Assume a curious non-expert. Define terms on first use. "
        "Use analogies. Build complexity gradually. Visuals or tables where concepts are abstract."
    ),
    "news_analysis": (
        "Invert pyramid: key facts first. Context second. Expert perspectives third. "
        "Implications last. Timely references and citations."
    ),
    "case_study": (
        "Problem → Approach → Results structure. Quantify outcomes. "
        "Include challenges faced. Make it replicable for the reader."
    ),
    "roundup": (
        "Curated list with editorial commentary. Each item: name, what it does, "
        "who it's for, standout feature. Intro and outro that synthesize themes."
    ),
    "general": (
        "Use the most logical structure for the topic. "
        "Intro → Core sections → Actionable takeaway → Conclusion."
    ),
}

_LOCALE_GUIDES: dict[str, str] = {
    "india": (
        "Use INR (₹) for all pricing. Reference Indian cities, states, and regulations. "
        "Use Indian brands and platforms as examples. Indian English spelling and terminology. "
        "Include India-specific market data, adoption rates, and pain points. "
        "Never use Western-centric examples unless directly compared to Indian equivalents."
    ),
    "us": (
        "Use USD ($) for all pricing. Reference US cities, states, and federal regulations. "
        "Use US brands and platforms. American English spelling. "
        "Include US market data and cultural context."
    ),
    "uk": (
        "Use GBP (£) for all pricing. Reference UK regions and regulations (FCA, GDPR etc). "
        "Use British English spelling. Include UK-specific market context."
    ),
    "global": (
        "Use USD ($) as the default currency, noting regional variation where relevant. "
        "Use globally recognized brands and platforms. Neutral English. "
        "Avoid cultural assumptions; favor universal examples."
    ),
}


def _locale_block(location: str) -> str:
    key = location.strip().lower()
    for loc, guide in _LOCALE_GUIDES.items():
        if loc in key:
            return guide
    # Fallback: treat as a custom region
    return (
        f"Localize all content for {location}: use the appropriate local currency, "
        f"reference local brands/regulations, and use culturally relevant examples."
    )


def _blog_type_block(blog_type: str) -> str:
    return _BLOG_TYPE_GUIDES.get(blog_type.lower().replace("-", "_"), _BLOG_TYPE_GUIDES["general"])


# ══════════════════════════════════════════════════════════════════════════════
# MAIN BLOG GENERATION PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

def blog_generation_prompts(
    keyword: str,
    secondary_keywords: list[str],
    location: str,
    word_count: int,
    tone: str,
    content_gaps: list[str],
    serp_personality: str,
    winning_angle: str,
    competitor_gaps: list[str],
    internal_links: list[dict],
    title: str | None = None,
    missing_keywords: list[str] = [],
    competitor_insights: str = "",
    web_search_context: str = "",
    blog_type: str = "general",          # tutorial | listicle | comparison | explainer | opinion_editorial | news_analysis | case_study | roundup | general
    audience: str = "general readers",   # e.g. "startup founders", "beginner developers", "HR professionals"
    is_coding_topic: bool | None = None, # None = auto-detect from keyword
    custom_locale_guide: str | None = None,  # override locale guide entirely
) -> tuple[str, str]:

    # ── Derived values ─────────────────────────────────────────────────────
    secondary_str = ", ".join([str(k) for k in secondary_keywords]) if secondary_keywords else "none"
    gaps_str      = "\n".join(f"- {g}" for g in [str(g) for g in content_gaps]) if content_gaps else "- Use your expertise to identify gaps"
    comp_gaps_str = "\n".join(f"- {g}" for g in [str(g) for g in competitor_gaps]) if competitor_gaps else "- None specified"
    missing_kw_str = "\n".join(f"- {kw}" for kw in [str(kw) for kw in missing_keywords]) if missing_keywords else "- None specified"
    il_str        = (
        "\n".join(f"- [{l['title']}]({l['url']})" for l in internal_links)
        if internal_links else "None provided"
    )
    title_instruction = (
        f'Use this exact title: "{title}"'
        if title
        else f'Create an SEO-optimized H1 title that naturally contains "{keyword}"'
    )

    locale_guide  = custom_locale_guide or _locale_block(location)
    type_guide    = _blog_type_block(blog_type)

    # Auto-detect coding topic from keyword if not specified
    coding_keywords = {"python", "javascript", "code", "programming", "api", "sql", "react", "django", "nodejs", "typescript", "rust", "golang", "bash", "cli", "docker", "kubernetes"}
    if is_coding_topic is None:
        is_coding_topic = any(ck in keyword.lower() for ck in coding_keywords)

    coding_instruction = (
        "Include 2–3 practical, well-commented code snippets using triple backticks with language identifiers. "
        "Code must be runnable and address real use cases from the blog."
        if is_coding_topic
        else "This is not a coding topic — do NOT insert code blocks."
    )

    low  = int(word_count * 0.97)
    high = int(word_count * 1.03)

    # ── System prompt ───────────────────────────────────────────────────────
    system = f"""You are a world-class SEO content strategist and writer.

YOUR GOAL: Write a {word_count}-word blog post that ranks on Google, genuinely helps the reader, and earns shares.

WRITING STYLE:
- Tone: {tone}
- Audience: {audience}
- Sound human: vary sentence lengths drastically (3-word sentences alongside 25-word ones), use rhetorical questions, specific examples, and occasional first-person observations
- NO AI clichés: never write "In conclusion", "It is worth noting", "Delve into", "In today's digital landscape", "As mentioned earlier", "It's worth mentioning", or "At the end of the day"
- Be direct: say what you mean in the fewest words that preserve meaning

LOCALIZATION — {location.upper()}:
{locale_guide}

BLOG TYPE — {blog_type.upper()}:
{type_guide}

FORMATTING RULES:
- Markdown only: # H1, ## H2, ### H3, **bold**, bullet lists, numbered lists, blockquotes
- Meta description in a blockquote labeled "META:" at the very top (150–160 chars)
- One paragraph (40–60 words) labeled <!-- SNIPPET --> optimized as a Google Featured Snippet direct answer
- Tables: only if they genuinely aid comprehension — never forced
- {coding_instruction}

WORD COUNT:
- Target: {word_count} words (body only — excluding META block)
- Acceptable range: {low}–{high} words
- Strategy: depth over padding. Add detail, examples, and nuance rather than repeating points
- Do NOT state the word count anywhere in the content"""

    # ── User prompt ─────────────────────────────────────────────────────────
    user = f"""Write a complete, publish-ready blog post with the following spec:

━━━ CORE BRIEF ━━━
PRIMARY KEYWORD    : {keyword}
SECONDARY KEYWORDS : {secondary_str}
TARGET LOCATION    : {location}
BLOG TYPE          : {blog_type}
SERP FORMAT        : {serp_personality}
WINNING ANGLE      : {winning_angle}
WORD COUNT         : {word_count} words (range: {low}–{high})
TITLE INSTRUCTION  : {title_instruction}

━━━ CONTENT STRATEGY ━━━
CONTENT GAPS TO COVER (that competitors missed):
{gaps_str}

ADDITIONAL COMPETITOR WEAKNESSES TO EXPLOIT:
{comp_gaps_str}

MISSING KEYWORDS TO INCORPORATE (competitors under-covered these):
{missing_kw_str}

━━━ LATEST WEB INFORMATION ━━━
{web_search_context if web_search_context else "(No web search data available)"}

━━━ COMPETITOR INSIGHTS ━━━
{competitor_insights}

━━━ INTERNAL LINKS ━━━

━━━ MANDATORY STRUCTURE ━━━
1.  META block (blockquote, 150–160 chars)
2.  H1 containing primary keyword
3.  Intro (120–180 words) — primary keyword in first 100 words, hook the reader immediately
4.  <!-- SNIPPET --> paragraph (40–60 words) — direct, snippet-ready answer to the main query
5.  At least 6 H2 sections (each 300–500 words with substance, not padding)
6.  At least 2 H3 subsections nested within H2s
7.  One numbered list (5–8 items) and one bullet list (5–8 items) — placed where they add most value
8.  Code snippets — {'YES: 2–3 practical snippets' if is_coding_topic else 'NO: skip entirely'}
9.  Comparison/reference table — only if it genuinely helps (optional)
10. CTA section at the end (50–80 words, actionable, relevant to the topic)

━━━ KEYWORD USAGE ━━━
- Primary keyword "{keyword}": intro, at least one H2, conclusion, naturally throughout
- Each secondary keyword: minimum 3–5 natural mentions each
- Do NOT keyword-stuff — write for humans first

━━━ QUALITY CHECKLIST (internalize before writing) ━━━
□ Every section answers a real question the reader has
□ Every example is specific, not generic
□ No sentence is padding — each earns its place
□ Localization feels native, not translated
□ The blog is better than any current top-10 result for this keyword

Write the complete blog now:"""

    return system, user


# ══════════════════════════════════════════════════════════════════════════════
# HUMANIZATION PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

def humanization_prompts(
    content: str,
    ai_flags: list[str],
    tone: str = "conversational",
    audience: str = "general readers",
    keyword: str = "",
) -> tuple[str, str]:
    flags_str = "\n".join(f"- {f}" for f in ai_flags) if ai_flags else "- General AI uniformity detected"

    system = f"""You are a senior human editor rewriting AI-generated blog content.

YOUR ONLY JOB: Make the writing feel like it came from a knowledgeable human, not a language model.

EDITING PRINCIPLES:
- Tone target: {tone} | Audience: {audience}
- Vary rhythm: mix short punchy sentences (3–8 words) with longer explanatory ones (20–30 words)
- Add specific, concrete detail instead of vague generalities
- Insert rhetorical questions, mild opinions, and first-person observations where natural
- Break up long uniform paragraphs — 2–4 sentences max per paragraph is often better
- Remove ALL AI clichés (see banned list below)
- Rewrite any robotic transitions into natural spoken phrasing
- Keep semantic meaning identical, but rewrite sentence construction aggressively where needed

BANNED PHRASES — delete or rewrite on sight:
"In conclusion" | "It is worth noting" | "Delve into" | "In today's world" |
"As mentioned earlier" | "It's important to note" | "Furthermore" (at sentence start) |
"Moreover" (at sentence start) | "In summary" | "To summarize" | "Needless to say" |
"At the end of the day" | "Moving forward" | "In the realm of"

STRICT PRESERVATION RULES — do NOT change:
- All headings, H1/H2/H3 structure
- Primary and secondary keyword placements
- All internal links (anchor text + URL)
- The META block
- The <!-- SNIPPET --> paragraph (only light touch allowed)
- Code snippets
- Tables
- Factual content and data
- Overall word count (±5% tolerance)

Return the full rewritten blog in markdown."""

    user = f"""Rewrite the blog below to sound authentically human.

DETECTED AI PATTERNS TO FIX:
{flags_str}

PRIMARY KEYWORD (preserve placements): {keyword if keyword else "see original"}

ORIGINAL BLOG:
{content}

Execution requirements:
1) First, silently identify AI-like lines (uniform sentence rhythm, template transitions, generic filler).
2) Then rewrite those lines with concrete, human phrasing and varied cadence.
3) Prefer active voice and specific verbs.
4) Do not return analysis. Return only final rewritten markdown.

Rewrite the COMPLETE blog now — every section, preserving all structure and SEO elements:"""

    return system, user


# ══════════════════════════════════════════════════════════════════════════════
# SNIPPET OPTIMIZATION PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

def snippet_optimization_prompts(
    keyword: str,
    context: str,
    snippet_section: str | None = None,  # Pass the <!-- SNIPPET --> paragraph if extracted
    blog_type: str = "general",
) -> tuple[str, str]:
    """
    snippet_section: the extracted <!-- SNIPPET --> content from the blog (preferred)
    context: full or partial blog content as fallback
    """

    # Prefer the dedicated snippet paragraph; fall back to first 2000 chars of content
    source_text = snippet_section if snippet_section else context[:2000]

    query_intent_hint = {
        "tutorial":           "The user wants to know HOW to do something.",
        "comparison":         "The user wants to know WHICH option is better.",
        "explainer":          "The user wants to know WHAT something is.",
        "listicle":           "The user wants a list of options or steps.",
        "opinion_editorial":  "The user wants an expert perspective.",
        "news_analysis":      "The user wants to understand recent events.",
        "case_study":         "The user wants real-world results and lessons.",
        "roundup":            "The user wants the best options curated.",
        "general":            "Infer intent from the keyword.",
    }.get(blog_type.lower().replace("-", "_"), "Infer intent from the keyword.")

    system = f"""You are a Google featured snippet optimization specialist.

QUERY INTENT FOR THIS BLOG TYPE ({blog_type}): {query_intent_hint}

You produce 3 snippet variants (paragraph, list, table) that compete for Google's featured snippet box.
Each variant must:
- Directly answer "{keyword}" in the first sentence
- Be self-contained (readable out of context)
- Avoid promotional language
- Match the likely SERP intent

Return ONLY valid JSON — no preamble, no markdown backticks."""

    user = f"""KEYWORD: "{keyword}"

SOURCE CONTENT:
{source_text}

Return this exact JSON:
{{
  "paragraph_variant": "<40-60 word direct answer — definition or explanation format>",
  "list_variant": "<numbered list, 4-6 items, each item one clear action or fact>",
  "table_variant": "<markdown table if a comparison or structured data fits, else null>",
  "readiness_score": <integer 0-100, likelihood this content wins featured snippet>,
  "primary_format_recommendation": "<paragraph | list | table>",
  "optimization_tips": [
    "<specific actionable tip 1>",
    "<specific actionable tip 2>",
    "<specific actionable tip 3>"
  ]
}}"""

    return system, user


# ══════════════════════════════════════════════════════════════════════════════
# TITLE & META GENERATION PROMPTS  (new — standalone utility)
# ══════════════════════════════════════════════════════════════════════════════

def title_meta_prompts(
    keyword: str,
    secondary_keywords: list[str],
    blog_type: str = "general",
    tone: str = "informational",
    location: str = "global",
    count: int = 5,
) -> tuple[str, str]:
    """Generate multiple title + meta description options for A/B testing."""

    secondary_str = ", ".join([str(k) for k in secondary_keywords[:5]]) if secondary_keywords else "none"

    system = """You are an SEO copywriter specializing in click-through rate optimization.
You generate title and meta description variants for A/B testing.
Return ONLY valid JSON."""

    user = f"""Generate {count} title + meta description pairs for:

KEYWORD       : {keyword}
SECONDARY     : {secondary_str}
BLOG TYPE     : {blog_type}
TONE          : {tone}
LOCATION      : {location}

Rules:
- Each title: 50–60 chars, contains primary keyword, compelling and specific
- Each meta: 150–160 chars, contains primary keyword + one secondary keyword, ends with a subtle CTA
- Vary the angle: use numbers, questions, "how to", superlatives, controversy, and benefit-led approaches
- Location-relevant where appropriate

Return:
{{
  "variants": [
    {{
      "title": "<title>",
      "meta": "<meta description>",
      "angle": "<one-word description of the angle: e.g. curiosity | authority | urgency | how-to | list>"
    }}
  ]
}}"""

    return system, user


# ══════════════════════════════════════════════════════════════════════════════
# OUTLINE GENERATION PROMPTS  (new — pre-writing step)
# ══════════════════════════════════════════════════════════════════════════════

def outline_generation_prompts(
    keyword: str,
    secondary_keywords: list[str],
    blog_type: str = "general",
    word_count: int = 1500,
    winning_angle: str = "",
    content_gaps: list[str] | None = None,
    location: str = "global",
    audience: str = "general readers",
) -> tuple[str, str]:
    """Generate a structured outline before full blog generation — improves coherence."""

    secondary_str = ", ".join([str(k) for k in secondary_keywords]) if secondary_keywords else "none"
    gaps_str      = "\n".join(f"- {g}" for g in [str(g) for g in content_gaps]) if content_gaps else "- None specified"

    system = """You are an SEO content strategist.
You create tight, logical blog outlines that maximize topical authority and reader satisfaction.
Return ONLY valid JSON."""

    user = f"""Create a detailed blog outline for:

KEYWORD       : {keyword}
SECONDARY     : {secondary_str}
BLOG TYPE     : {blog_type}
WORD COUNT    : {word_count}
WINNING ANGLE : {winning_angle}
LOCATION      : {location}
AUDIENCE      : {audience}

CONTENT GAPS TO COVER:
{gaps_str}

Return:
{{
  "suggested_title": "<SEO title>",
  "meta_description": "<150-160 char meta>",
  "intro_hook": "<1-2 sentence description of how to open>",
  "snippet_target": "<the specific question this blog should win a featured snippet for>",
  "sections": [
    {{
      "h2": "<H2 heading>",
      "target_words": <int>,
      "subsections": ["<H3 idea 1>", "<H3 idea 2>"],
      "key_points": ["<point 1>", "<point 2>", "<point 3>"],
      "keywords_to_include": ["<keyword>"]
    }}
  ],
  "cta_direction": "<what the CTA should push the reader to do>",
  "tables_needed": <true|false>,
  "code_snippets_needed": <true|false>,
  "estimated_sections": <int>
}}"""

    return system, user


# ══════════════════════════════════════════════════════════════════════════════
# INTERNAL LINKING PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

def internal_linking_prompts(content: str, existing_blogs: list[dict], primary_keyword: str) -> tuple[str, str]:
    # Build blogs string with defensive type handling
    blogs_str_items = []
    for b in existing_blogs:
        title = b.get('title', '')
        url = b.get('url', '')
        topic = b.get('topic', '')
        keywords = b.get('keywords', [])
        
        # Ensure keywords is a list of strings
        if isinstance(keywords, str):
            keywords_str = keywords
        elif isinstance(keywords, list):
            keywords_str = ', '.join(str(k) for k in keywords)
        else:
            keywords_str = ''
        
        blogs_str_items.append(f"- Title: {title} | URL: {url} | Topic: {topic} | Keywords: {keywords_str}")
    
    blogs_str = "\n".join(blogs_str_items)

    system = """You are an internal linking strategist for an SEO blog platform.
You identify the best anchor texts and placements to link related blog posts.
Return valid JSON only."""

    user = f"""Primary blog keyword: "{primary_keyword}"

EXISTING BLOG POSTS TO LINK FROM:
{blogs_str}

BLOG CONTENT (first 2000 chars):
{content[:2000]}

Suggest internal link placements. Return this JSON:
{{
  "suggestions": [
    {{
      "anchor_text": "<exact text to hyperlink>",
      "target_url": "<url from above list>",
      "target_title": "<blog title>",
      "relevance_score": <float 0-10>,
      "placement_hint": "<sentence or paragraph context where this link fits>",
      "reason": "<why this link adds value>"
    }}
  ],
  "linking_score": <float 0-100>
}}"""

    return system, user


# ══════════════════════════════════════════════════════════════════════════════
# TITLE & META GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def title_meta_prompts(keyword: str, content_summary: str, location: str) -> tuple[str, str]:
    system = """You are an SEO title and meta description expert.
Return valid JSON only."""

    user = f"""Keyword: "{keyword}" | Location: "{location}"
Content summary: {content_summary[:500]}

Generate:
- title: SEO-optimized H1 (50-60 chars, includes keyword)
- meta_description: 150-160 chars, includes keyword, has CTA
- slug: URL-friendly slug

Return JSON: {{"title": "", "meta_description": "", "slug": ""}}"""

    return system, user
