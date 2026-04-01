#!/usr/bin/env python3
"""
Hashnode Integration Examples
==============================
Complete examples showing how to use the Hashnode publishing features.
"""

import asyncio
import httpx
import json

# Configuration
BASE_URL = "http://localhost:8000"


# ─────────────────────────────────────────────────────────────────────────────
# Example 1: Generate Blog + Auto-Publish to Hashnode
# ─────────────────────────────────────────────────────────────────────────────
async def example_generate_and_publish():
    """Generate a blog and automatically publish to Hashnode"""
    
    print("=" * 70)
    print("EXAMPLE 1: Generate Blog + Auto-Publish to Hashnode")
    print("=" * 70)
    
    request_payload = {
        "keyword": "Python Data Science Tutorial",
        "secondary_keywords": ["pandas", "numpy", "data analysis"],
        "word_count": 2500,
        "tone": "educational",
        "publish_to_hashnode": True,  # ← Enable Hashnode publishing
        "hashnode_tags": ["python", "data-science", "tutorial"],
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/blog/generate",
            json=request_payload,
            timeout=60.0,
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Blog Generated Successfully")
            print(f"   Title: {result.get('title')}")
            print(f"   Word Count: {result.get('word_count')}")
            print(f"   SEO Score: {result.get('seo_score').get('overall_score')}")
            print(f"   Blog ID: {result.get('blog_id')}")
            
            # Check Hashnode publishing result
            hashnode = result.get("hashnode_publish")
            if hashnode:
                if hashnode.get("success"):
                    print(f"\n✅ Published to Hashnode")
                    print(f"   URL: {hashnode.get('hashnode_url')}")
                    print(f"   Hashnode ID: {hashnode.get('hashnode_id')}")
                else:
                    print(f"\n⚠️  Hashnode Publishing Failed")
                    print(f"   Error: {hashnode.get('error')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")


# ─────────────────────────────────────────────────────────────────────────────
# Example 2: Publish Existing Blog to Hashnode
# ─────────────────────────────────────────────────────────────────────────────
async def example_publish_existing_blog():
    """Publish an already-generated blog to Hashnode"""
    
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Publish Existing Blog to Hashnode")
    print("=" * 70)
    
    # First, get the list of blogs
    print("\n1️⃣  Fetching list of unpublished blogs...")
    
    async with httpx.AsyncClient() as client:
        # Get blogs
        list_response = await client.get(f"{BASE_URL}/blog/list?limit=10")
        
        if list_response.status_code != 200:
            print(f"❌ Failed to fetch blogs")
            return
        
        blogs = list_response.json()
        
        if not blogs:
            print("❌ No blogs found")
            return
        
        print(f"   Found {len(blogs)} blogs")
        
        # Pick the first blog
        first_blog = blogs[0]
        blog_id = first_blog["id"]
        
        print(f"\n2️⃣  Publishing blog to Hashnode...")
        print(f"   Blog: {first_blog['title']}")
        print(f"   Blog ID: {blog_id}")
        
        # Publish to Hashnode
        publish_payload = {
            "tags": ["ai", "automation", "blog-generation"]
        }
        
        publish_response = await client.put(
            f"{BASE_URL}/blog/{blog_id}/publish-hashnode",
            json=publish_payload,
            timeout=30.0,
        )
        
        if publish_response.status_code == 200:
            result = publish_response.json()
            
            if result.get("status") == "already_published":
                print(f"\n⚠️  Blog Already Published")
                print(f"   URL: {result.get('hashnode_url')}")
            else:
                print(f"\n✅ Blog Published Successfully")
                print(f"   URL: {result.get('hashnode_url')}")
                print(f"   Hashnode ID: {result.get('hashnode_id')}")
        else:
            print(f"\n❌ Error: {publish_response.status_code}")
            print(f"   {publish_response.text}")


# ─────────────────────────────────────────────────────────────────────────────
# Example 3: Batch Publish Multiple Blogs
# ─────────────────────────────────────────────────────────────────────────────
async def example_batch_publish():
    """Publish multiple blogs to Hashnode with rate limiting"""
    
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Batch Publish Multiple Blogs")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        # Get all unpublished blogs
        print("\n1️⃣  Fetching unpublished blogs...")
        
        list_response = await client.get(f"{BASE_URL}/blog/list?limit=100")
        
        if list_response.status_code != 200:
            print(f"❌ Failed to fetch blogs")
            return
        
        blogs = list_response.json()
        print(f"   Found {len(blogs)} blogs")
        
        # Publish each one with rate limiting (2 second delay)
        published_count = 0
        failed_count = 0
        already_published_count = 0
        
        for i, blog in enumerate(blogs, 1):
            blog_id = blog["id"]
            blog_title = blog["title"]
            
            print(f"\n{i}. Publishing: {blog_title}")
            
            try:
                publish_response = await client.put(
                    f"{BASE_URL}/blog/{blog_id}/publish-hashnode",
                    json={"tags": ["auto-published", "blogy"]},
                    timeout=30.0,
                )
                
                if publish_response.status_code == 200:
                    result = publish_response.json()
                    
                    if result.get("status") == "published":
                        print(f"   ✅ Published: {result.get('hashnode_url')}")
                        published_count += 1
                    else:
                        print(f"   ℹ️  Already published")
                        already_published_count += 1
                else:
                    print(f"   ❌ Failed: {publish_response.status_code}")
                    failed_count += 1
                
                # Rate limiting: wait 2 seconds between requests
                if i < len(blogs):
                    await asyncio.sleep(2)
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                failed_count += 1
        
        # Summary
        print(f"\n" + "=" * 70)
        print("Batch Publish Summary")
        print("=" * 70)
        print(f"   Successfully Published: {published_count}")
        print(f"   Already Published: {already_published_count}")
        print(f"   Failed: {failed_count}")
        print(f"   Total: {len(blogs)}")


# ─────────────────────────────────────────────────────────────────────────────
# Example 4: Generate with Custom Configuration
# ─────────────────────────────────────────────────────────────────────────────
async def example_custom_generation():
    """Generate a blog with advanced options including Hashnode tags"""
    
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Generate Blog with Custom Hashnode Tags")
    print("=" * 70)
    
    request_payload = {
        "keyword": "Web Performance Optimization",
        "secondary_keywords": [
            "Core Web Vitals",
            "Page Speed",
            "Lighthouse",
            "Performance Budget"
        ],
        "target_location": "USA",
        "word_count": 3000,
        "tone": "professional",
        "enable_humanization": True,
        "publish_to_hashnode": True,
        "hashnode_tags": [
            "web-performance",
            "frontend",
            "optimization",
            "seo",
            "performance"
        ],
    }
    
    print(f"\n📝 Request Configuration:")
    print(f"   Keyword: {request_payload['keyword']}")
    print(f"   Word Count: {request_payload['word_count']}")
    print(f"   Hashnode Tags: {', '.join(request_payload['hashnode_tags'])}")
    
    async with httpx.AsyncClient() as client:
        print(f"\n⏳ Generating blog (this may take a minute)...")
        
        response = await client.post(
            f"{BASE_URL}/blog/generate",
            json=request_payload,
            timeout=120.0,  # Longer timeout for generation
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Generation Complete")
            print(f"   Title: {result.get('title')}")
            print(f"   Slug: {result.get('slug')}")
            print(f"   Word Count: {result.get('word_count')}")
            print(f"   Generation Time: {result.get('generation_time_seconds')}s")
            
            # SEO Score
            seo = result.get('seo_score', {})
            print(f"\n📊 SEO Metrics:")
            print(f"   Overall Score: {seo.get('overall_score', 'N/A')}/100")
            print(f"   Readability Score: {seo.get('readability_score', 'N/A')}/100")
            print(f"   Keyword in Title: {'✅' if seo.get('keyword_in_title') else '❌'}")
            
            # AI Detection
            ai = result.get('ai_detection', {})
            print(f"\n🤖 AI Detection:")
            print(f"   AI Probability: {ai.get('ai_probability_percent', 'N/A')}%")
            print(f"   Naturalness Score: {ai.get('naturalness_score', 'N/A')}/100")
            print(f"   Verdict: {ai.get('verdict', 'N/A')}")
            
            # Hashnode Publishing
            hashnode = result.get('hashnode_publish')
            if hashnode:
                print(f"\n🔗 Hashnode Publishing:")
                if hashnode.get('success'):
                    print(f"   ✅ Successfully Published")
                    print(f"   URL: {hashnode.get('hashnode_url')}")
                    print(f"   ID: {hashnode.get('hashnode_id')}")
                else:
                    print(f"   ❌ Publishing Failed")
                    print(f"   Error: {hashnode.get('error')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")


# ─────────────────────────────────────────────────────────────────────────────
# Main Menu
# ─────────────────────────────────────────────────────────────────────────────
async def main():
    """Main example menu"""
    
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Hashnode Integration Examples" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    
    examples = {
        "1": ("Generate Blog + Auto-Publish", example_generate_and_publish),
        "2": ("Publish Existing Blog", example_publish_existing_blog),
        "3": ("Batch Publish Multiple Blogs", example_batch_publish),
        "4": ("Custom Generation & Publishing", example_custom_generation),
    }
    
    print("\nChoose an example to run:")
    for key, (name, _) in examples.items():
        print(f"   {key}. {name}")
    print("   5. Run all examples")
    print("   q. Quit\n")
    
    choice = input("Enter your choice: ").strip().lower()
    
    if choice == "q":
        print("Goodbye!")
        return
    
    if choice == "5":
        for name, func in examples.values():
            await func()
    elif choice in examples:
        _, func = examples[choice]
        await func()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
