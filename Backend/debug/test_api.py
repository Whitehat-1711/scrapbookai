"""
test_api.py — Quick end-to-end test for all Blogy API endpoints.
Run after starting the server:
    python test_api.py
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"
TIMEOUT = 120.0  # Blog generation can take up to 60s


async def test_health():
    print("\n── Health Check ─────────────────────────────────────")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(f"{BASE_URL}/health")
        print(f"Status: {r.status_code}")
        print(json.dumps(r.json(), indent=2))


async def test_keyword_cluster():
    print("\n── Keyword Clustering ───────────────────────────────")
    payload = {
        "seed_keyword": "AI blog automation tool",
        "target_location": "India",
        "cluster_count": 4,
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(f"{BASE_URL}/keywords/cluster", json=payload)
        print(f"Status: {r.status_code}")
        data = r.json()
        print(f"Total keywords: {data.get('total_keywords')}")
        print(f"Recommended primary: {data.get('recommended_primary')}")
        print(f"Traffic potential: {data.get('traffic_potential')}")
        for c in data.get("clusters", [])[:2]:
            print(f"  • {c['cluster_name']} ({c['intent']}) — {c['estimated_monthly_searches']}")


async def test_serp_analysis():
    print("\n── SERP Gap Analysis ────────────────────────────────")
    payload = {
        "keyword": "best SEO tool for bloggers India",
        "target_location": "India",
        "max_results": 5,
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(f"{BASE_URL}/serp/analyze", json=payload)
        print(f"Status: {r.status_code}")
        data = r.json()
        print(f"SERP Personality: {data.get('serp_personality')}")
        print(f"Recommended format: {data.get('recommended_format')}")
        print(f"Recommended word count: {data.get('recommended_word_count')}")
        print(f"Winning angle: {data.get('winning_angle')}")
        print("Content Gaps:")
        for g in data.get("content_gaps", [])[:3]:
            print(f"  [{g['importance'].upper()}] {g['topic']}")


async def test_seo_analyze():
    print("\n── SEO Analysis ─────────────────────────────────────")
    sample_content = """# Best AI Blog Automation Tool in India

AI blog automation tools are transforming how Indian content creators and businesses scale their SEO strategy.

## Why AI Blog Automation Matters

The best AI blog automation tool helps you save time, reduce costs, and produce high-quality content at scale.

## Top Features to Look For

- Keyword clustering and intent mapping
- SERP gap analysis
- Featured snippet optimization
- AI humanization pipeline

## AI Blog Automation in the Indian Market

India's digital marketing landscape is growing rapidly. AI blog automation tools designed for Indian SEO needs
offer significant advantages over generic global tools.

## Pricing and Value

Most AI blog automation tools offer tiered pricing. Indian businesses can find cost-effective solutions.

## Conclusion

Choosing the right AI blog automation tool India can transform your content strategy.
"""
    payload = {
        "content": sample_content,
        "keyword": "AI blog automation tool India",
        "secondary_keywords": ["blog automation", "SEO tool India"],
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(f"{BASE_URL}/seo/analyze", json=payload)
        print(f"Status: {r.status_code}")
        data = r.json()
        print(f"Overall SEO Score: {data.get('overall_score')}/100")
        print(f"Word Count: {data.get('word_count')}")
        print(f"Readability: {data.get('readability_score')} ({data.get('readability_grade')})")
        print(f"Traffic Potential: {data.get('projected_traffic_potential')}")
        print(f"Issues: {len(data.get('issues', []))}")
        for issue in data.get("issues", [])[:3]:
            print(f"  ⚠ {issue}")


async def test_ai_detection():
    print("\n── AI Detection ─────────────────────────────────────")
    sample = """In today's rapidly evolving digital landscape, it is worth noting that AI blog automation 
    tools are playing a pivotal role in content marketing. These robust solutions seamlessly integrate 
    with existing workflows, fostering greater productivity and enabling teams to harness the power of 
    artificial intelligence. In conclusion, delving into these tools can help businesses navigate the 
    complex realm of digital marketing."""

    payload = {"content": sample}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(f"{BASE_URL}/seo/detect-ai", json=payload)
        print(f"Status: {r.status_code}")
        data = r.json()
        print(f"AI Probability: {data.get('ai_probability_percent')}%")
        print(f"Naturalness Score: {data.get('naturalness_score')}/100")
        print(f"Burstiness: {data.get('burstiness_score')}")
        print(f"Verdict: {data.get('verdict')}")
        print(f"Flags: {len(data.get('flags', []))}")
        for flag in data.get("flags", [])[:3]:
            print(f"  🚩 {flag}")


async def test_humanize():
    print("\n── Humanization ─────────────────────────────────────")
    ai_text = """In today's digital world, it is important to note that blogging has become a pivotal 
    component of content marketing strategies. Businesses can leverage robust AI tools to seamlessly 
    generate high-quality content. This approach fosters greater efficiency and allows teams to harness 
    the power of automation. In conclusion, embracing these solutions is essential for navigating the 
    ever-changing landscape of digital marketing."""

    payload = {"content": ai_text, "force": True}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(f"{BASE_URL}/humanize", json=payload)
        print(f"Status: {r.status_code}")
        data = r.json()
        print(f"Original AI %: {data.get('original_ai_probability')}%")
        print(f"Final AI %:    {data.get('final_ai_probability')}%")
        print(f"Improvement:   {data.get('naturalness_improvement')} points")
        print(f"Was Humanized: {data.get('was_humanized')}")


async def test_full_blog_generation():
    print("\n── Full Blog Generation Pipeline ────────────────────")
    print("(This may take 30-90 seconds...)")
    payload = {
        "keyword": "Blogy best AI blog automation tool India",
        "secondary_keywords": [
            "AI blog writer India",
            "SEO automation tool",
            "blog content generator",
            "affordable SEO tool India",
        ],
        "target_location": "India",
        "blog_title": "Blogy – Best AI Blog Automation Tool in India",
        "word_count": 2500,
        "tone": "professional",
        "competitor_urls": [],
        "internal_links": [
            {
                "title": "How to Rank on Google India",
                "url": "https://blogy.in/blog/rank-google-india",
                "topic": "SEO strategy",
                "keywords": ["Google ranking India", "SEO tips"],
            },
            {
                "title": "Content Marketing for Indian Startups",
                "url": "https://blogy.in/blog/content-marketing-india",
                "topic": "content marketing",
                "keywords": ["content marketing India", "startup marketing"],
            },
        ],
        "enable_humanization": True,
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(f"{BASE_URL}/blog/generate", json=payload)
        print(f"Status: {r.status_code}")
        if r.status_code != 200:
            print(f"Error: {r.text[:500]}")
            return

        data = r.json()
        print(f"\n📝 Title: {data.get('title')}")
        print(f"🔗 Slug: {data.get('slug')}")
        print(f"📄 Word Count: {data.get('word_count')}")
        print(f"⏱  Generation Time: {data.get('generation_time_seconds')}s")

        seo = data.get("seo_score", {})
        print(f"\n📊 SEO Score: {seo.get('overall_score')}/100")
        print(f"   Readability: {seo.get('readability_score')} ({seo.get('readability_grade')})")
        print(f"   Headings: {seo.get('heading_count')}")
        print(f"   Internal Links: {seo.get('internal_link_count')}")
        print(f"   Traffic Potential: {seo.get('projected_traffic_potential')}")

        ai = data.get("ai_detection", {})
        print(f"\n🤖 AI Detection: {ai.get('ai_probability_percent')}%")
        print(f"   Naturalness: {ai.get('naturalness_score')}/100")
        print(f"   Verdict: {ai.get('verdict')}")

        snippet = data.get("snippet_optimization", {})
        print(f"\n✂  Snippet Readiness: {snippet.get('readiness_probability')}%")
        best = snippet.get("recommended_variant", {})
        print(f"   Best Variant: {best.get('type')} ({best.get('snippet_score')} score)")

        links = data.get("internal_links", {})
        print(f"\n🔗 Internal Link Suggestions: {links.get('total_suggestions')}")
        print(f"   Linking Score: {links.get('linking_score')}/100")

        clusters = data.get("keyword_clusters")
        if clusters:
            print(f"\n🎯 Keyword Clusters: {len(clusters.get('clusters', []))}")
            print(f"   Total Keywords: {clusters.get('total_keywords')}")

        serp = data.get("serp_analysis")
        if serp:
            print(f"\n🔍 SERP Personality: {serp.get('serp_personality')}")
            print(f"   Content Gaps Found: {len(serp.get('content_gaps', []))}")

        print(f"\n--- META DESCRIPTION ---")
        print(data.get("meta_description"))
        print(f"\n--- CONTENT PREVIEW (first 500 chars) ---")
        print(data.get("content", "")[:500] + "...")


async def main():
    print("=" * 60)
    print("  BLOGY AI ENGINE — END-TO-END API TEST")
    print("=" * 60)

    await test_health()
    await test_keyword_cluster()
    await test_serp_analysis()
    await test_seo_analyze()
    await test_ai_detection()
    await test_humanize()
    await test_full_blog_generation()

    print("\n" + "=" * 60)
    print("  ALL TESTS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
