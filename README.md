# 🚀 Blogy AI Blog Engine

> **Groq-powered (llama-3.3-70b-versatile)** multi-agent SEO blog generation engine.
> Built for Bizmark'26 — Prompt & Profit hackathon.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                          │
│                                                                     │
│  POST /blog/generate  ←── Master pipeline (all agents in sequence) │
│  POST /keywords/cluster                                             │
│  POST /serp/analyze                                                 │
│  POST /seo/analyze   /detect-ai   /snippet   /links                │
│  POST /humanize                                                     │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
         ┌─────────────────────────▼─────────────────────────┐
         │              Orchestration Layer                   │
         │    asyncio.gather() — parallel agent execution     │
         └──┬──────────┬──────────┬──────────┬──────────┬───┘
            │          │          │          │          │
     ┌──────▼──┐ ┌─────▼───┐ ┌───▼────┐ ┌──▼──────┐ ┌▼────────┐
     │Keyword  │ │  SERP   │ │  Blog  │ │   SEO   │ │Humanize │
     │Cluster  │ │  Gap    │ │  Gen   │ │Optimizer│ │  Agent  │
     │  Agent  │ │ Agent   │ │ Agent  │ │  Agent  │ │         │
     └──────┬──┘ └─────┬───┘ └───┬────┘ └──┬──────┘ └┬────────┘
            │          │         │         │         │
            └──────────┴─────────┴─────────┴─────────┘
                                   │
                        ┌──────────▼──────────┐
                        │   Groq LLM Service  │
                        │ llama-3.3-70b-vers. │
                        └─────────────────────┘
```

---

## Metrics Covered

| Metric | Implementation |
|---|---|
| **Prompt Architecture Clarity** | Modular prompt templates in `prompts/prompts.py` |
| **Keyword Clustering Logic** | Intent-based clusters with traffic + difficulty |
| **SERP Gap Identification** | DuckDuckGo scrape + competitor page fetch + LLM analysis |
| **Projected Traffic Potential** | Weighted score → monthly visit range estimate |
| **SEO Optimization %** | Composite 0-100 score (density + readability + structure) |
| **AI Detection % & Naturalness** | Heuristic: burstiness + perplexity + AI phrase flags |
| **Snippet Readiness Probability** | 3-variant generation (paragraph/list/table) with scoring |
| **Keyword Density Compliance** | Per-keyword density with optimal/under/over status |
| **Internal Linking Logic** | LLM-powered semantic anchor text + placement suggestions |
| **Scalability & Replicability** | Stateless agents, async parallel execution, env config |

---

## Project Structure

```
blogy-ai-engine/
│
├── main.py                    # FastAPI app + router registration
├── config.py                  # All environment config
├── requirements.txt
├── .env.example
│
├── agents/                    # One file per agent
│   ├── keyword_agent.py       # Agent 1: Keyword clustering
│   ├── serp_agent.py          # Agent 2: SERP gap analysis
│   ├── blog_generator.py      # Agent 3: Blog generation
│   ├── seo_optimizer.py       # Agent 4: SEO scoring (deterministic)
│   ├── snippet_agent.py       # Agent 5: Featured snippet optimization
│   ├── humanizer.py           # Agent 6: AI humanization
│   └── internal_linking_agent.py  # Agent 7: Internal link suggestions
│
├── routers/                   # FastAPI route handlers
│   ├── blog.py                # POST /blog/generate
│   ├── keywords.py            # POST /keywords/cluster
│   ├── serp.py                # POST /serp/analyze
│   ├── seo.py                 # POST /seo/analyze|detect-ai|snippet|links
│   └── humanize.py            # POST /humanize
│
├── services/
│   ├── groq_service.py        # Groq async wrapper (chat_completion + json mode)
│   └── ai_detection_service.py  # Heuristic AI detection
│
├── models/
│   ├── request_models.py      # Pydantic request schemas
│   └── response_models.py     # Pydantic response schemas
│
├── prompts/
│   └── prompts.py             # All LLM prompt templates (system + user)
│
└── utils/
    ├── scraper.py             # Async DuckDuckGo scraper + page fetcher
    └── seo_utils.py           # Deterministic SEO calculations (no LLM)
```

---

## Quick Start

### 1. Clone & Install

```bash
git clone <repo>
cd blogy-ai-engine

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Run

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open: http://localhost:8000/docs

---

## API Reference

### POST `/blog/generate` — Full Pipeline

```json
{
  "keyword": "AI blog automation tool India",
  "secondary_keywords": ["blog automation", "SEO tool India", "AI content writer"],
  "target_location": "India",
  "word_count": 2500,
  "tone": "professional",
  "competitor_urls": [],
  "internal_links": [
    {
      "title": "How to Rank on Google in India",
      "url": "https://blogy.in/blog/rank-google-india",
      "topic": "SEO",
      "keywords": ["SEO", "Google ranking India"]
    }
  ],
  "enable_humanization": true
}
```

**Response includes:**
- `title`, `meta_description`, `slug`, `content`
- `seo_score` — Full SEO audit (0-100)
- `ai_detection` — AI probability + naturalness + flags
- `snippet_optimization` — 3 snippet variants + readiness score
- `internal_links` — Semantic link suggestions
- `keyword_clusters` — Intent-grouped keyword clusters
- `serp_analysis` — Competitor gaps + winning angle
- `generation_time_seconds`

---

### POST `/keywords/cluster`

```json
{
  "seed_keyword": "SEO tool",
  "target_location": "India",
  "cluster_count": 5
}
```

### POST `/serp/analyze`

```json
{
  "keyword": "best AI blog automation tool India",
  "target_location": "India",
  "max_results": 10
}
```

### POST `/seo/analyze`

```json
{
  "content": "# Your blog content here...",
  "keyword": "AI blog automation",
  "secondary_keywords": ["blog tool", "SEO automation"]
}
```

### POST `/seo/detect-ai`

```json
{
  "content": "Your blog content to check for AI patterns..."
}
```

### POST `/seo/snippet`

```json
{
  "content": "# Blog content...",
  "keyword": "AI blog automation tool"
}
```

### POST `/seo/links`

```json
{
  "content": "# Blog content...",
  "primary_keyword": "AI blog automation",
  "existing_blogs": [
    {
      "title": "How to Rank on Google",
      "url": "https://blogy.in/blog/rank-google",
      "topic": "SEO",
      "keywords": ["SEO", "Google ranking"]
    }
  ]
}
```

### POST `/humanize`

```json
{
  "content": "# AI-generated blog content...",
  "force": false
}
```

---

## AI Detection Algorithm

The heuristic AI detector doesn't need a paid API. It scores on 4 signals:

| Signal | Weight | What it measures |
|---|---|---|
| **Burstiness** | 35% | Sentence length variance — AI writes uniform lengths |
| **Perplexity Proxy** | 25% | Bigram uniqueness ratio — AI reuses transitions |
| **AI Phrase Flags** | 30% | 20 known AI clichés ("delve into", "in today's world", etc.) |
| **Paragraph Uniformity** | 10% | AI paragraphs are suspiciously equal in length |

---

## SEO Score Breakdown

| Component | Max Points | How |
|---|---|---|
| Word count ≥ 2,500 | 20 | Full marks for 2500+, partial for 1500+ |
| Keyword density 0.5-2.5% | 20 | Optimal range = full marks |
| Readability ≥ 60 | 15 | Flesch-Kincaid score |
| Headings ≥ 5 | 10 | H2/H3 structure |
| Keyword in title | 15 | Binary check |
| Keyword in first 100 words | 10 | Binary check |
| Internal links ≥ 3 | 5 | Markdown link count |
| LSI keywords ≥ 8 | 5 | Top co-occurring non-stopword terms |
| **Total** | **100** | |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ | Get from console.groq.com |
| `SERPAPI_KEY` | ❌ | Optional (uses DuckDuckGo scraper by default) |
| `APP_ENV` | ❌ | `development` / `production` |
| `APP_HOST` | ❌ | Default: `0.0.0.0` |
| `APP_PORT` | ❌ | Default: `8000` |
| `CORS_ORIGINS` | ❌ | Comma-separated frontend origins |
