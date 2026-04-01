#!/usr/bin/env python3
"""
Hashnode API Debug and Test Script
===================================
Tests the Hashnode GraphQL API directly to debug publishing issues.
"""

import asyncio
import httpx
import json
from ..core.config import HASHNODE_API_TOKEN, HASHNODE_PUBLICATION_ID

HASHNODE_API_URL = "https://gql.hashnode.com"


async def test_authentication():
    """Test if API token is valid"""
    print("🔐 Testing Authentication...")
    
    query = """
    query {
        me {
            id
            name
            username
        }
    }
    """
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            HASHNODE_API_URL,
            json={"query": query},
            headers={"Authorization": f"Bearer {HASHNODE_API_TOKEN}"},
            timeout=10.0,
        )
        
        print(f"   Status: {response.status_code}")
        data = response.json()
        
        if "errors" in data:
            print(f"   ❌ Error: {data['errors'][0]['message']}")
            return False
        
        user = data.get("data", {}).get("me", {})
        if user:
            print(f"   ✅ Authenticated as: {user.get('name')} (@{user.get('username')})")
            return True
        else:
            print(f"   ❌ No user data returned")
            return False


async def test_get_publications():
    """Get list of publications"""
    print("\n📚 Fetching Publications...")
    
    query = """
    query {
        me {
            publications(first: 5) {
                edges {
                    node {
                        id
                        displayTitle
                        slug
                    }
                }
            }
        }
    }
    """
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            HASHNODE_API_URL,
            json={"query": query},
            headers={"Authorization": f"Bearer {HASHNODE_API_TOKEN}"},
            timeout=10.0,
        )
        
        data = response.json()
        
        if "errors" in data:
            print(f"   ❌ Error: {data['errors'][0]['message']}")
            return None
        
        pubs = data.get("data", {}).get("me", {}).get("publications", {}).get("edges", [])
        
        if pubs:
            print(f"   ✅ Found {len(pubs)} publication(s):")
            for pub in pubs:
                node = pub.get("node", {})
                pub_id = node.get("id")
                pub_title = node.get("displayTitle")
                pub_slug = node.get("slug")
                
                # Check if this matches configured publication
                match = " ✓ MATCHED" if pub_id == HASHNODE_PUBLICATION_ID else ""
                print(f"      • {pub_title} (ID: {pub_id}){match}")
                print(f"        Slug: {pub_slug}")
            return pubs
        else:
            print(f"   ⚠️ No publications found")
            return None


async def test_publish_simple():
    """Test publishing a simple blog post"""
    print("\n📝 Testing Simple Blog Publication...")
    
    test_title = "Test Blog Post"
    test_slug = "test-blog-post"
    test_content = "# Test Content\n\nThis is a test blog post."
    test_subtitle = "A test blog"
    
    # Escape strings for GraphQL
    def escape(s):
        return (
            s.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t")
        )
    
    title_esc = escape(test_title)
    content_esc = escape(test_content)
    subtitle_esc = escape(test_subtitle)
    
    mutation = f"""
    mutation PublishPost {{
        publishPost(input: {{
            publicationId: "{HASHNODE_PUBLICATION_ID}"
            title: "{title_esc}"
            subtitle: "{subtitle_esc}"
            contentMarkdown: "{content_esc}"
            slug: "{test_slug}"
        }}) {{
            post {{
                id
                slug
                url
                title
            }}
        }}
    }}
    """
    
    print(f"   Mutation:\n{mutation}\n")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            HASHNODE_API_URL,
            json={"query": mutation},
            headers={"Authorization": f"Bearer {HASHNODE_API_TOKEN}"},
            timeout=10.0,
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response:\n{json.dumps(response.json(), indent=2)}\n")
        
        data = response.json()
        
        if "errors" in data:
            error = data["errors"][0]
            print(f"   ❌ GraphQL Error: {error.get('message')}")
            if "extensions" in error:
                print(f"      Details: {error['extensions']}")
            return False
        
        post = data.get("data", {}).get("publishPost", {}).get("post", {})
        if post:
            print(f"   ✅ Published successfully!")
            print(f"      URL: {post.get('url')}")
            print(f"      ID: {post.get('id')}")
            return True
        else:
            print(f"   ⚠️ No post data in response")
            return False


async def test_publish_with_tags():
    """Test publishing with tags"""
    print("\n🏷️  Testing Blog Publication with Tags...")
    
    test_title = "Test Blog with Tags"
    test_slug = "test-with-tags"
    test_content = "# Tagged Content\n\nThis blog has tags."
    test_subtitle = "Tagged test"
    test_tags = ["test", "debug"]
    
    def escape(s):
        return (
            s.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t")
        )
    
    title_esc = escape(test_title)
    content_esc = escape(test_content)
    subtitle_esc = escape(test_subtitle)
    
    tags_list = ", ".join([f'"{escape(tag)}"' for tag in test_tags])
    tags_input = f', tagSlugs: [{tags_list}]'
    
    mutation = f"""
    mutation PublishPost {{
        publishPost(input: {{
            publicationId: "{HASHNODE_PUBLICATION_ID}"
            title: "{title_esc}"
            subtitle: "{subtitle_esc}"
            contentMarkdown: "{content_esc}"
            slug: "{test_slug}"{tags_input}
        }}) {{
            post {{
                id
                slug
                url
                title
            }}
        }}
    }}
    """
    
    print(f"   Tags: {test_tags}")
    print(f"   Mutation:\n{mutation}\n")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            HASHNODE_API_URL,
            json={"query": mutation},
            headers={"Authorization": f"Bearer {HASHNODE_API_TOKEN}"},
            timeout=10.0,
        )
        
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response:\n{json.dumps(data, indent=2)}\n")
        
        if "errors" in data:
            error = data["errors"][0]
            print(f"   ❌ Error: {error.get('message')}")
            return False
        
        post = data.get("data", {}).get("publishPost", {}).get("post", {})
        if post:
            print(f"   ✅ Published with tags!")
            print(f"      URL: {post.get('url')}")
            return True
        else:
            print(f"   ⚠️ No post data in response")
            return False


async def main():
    """Run all tests"""
    print("=" * 70)
    print("Hashnode API Debug Tests")
    print("=" * 70)
    
    if not HASHNODE_API_TOKEN:
        print("❌ HASHNODE_API_TOKEN not set in .env")
        return
    
    if not HASHNODE_PUBLICATION_ID:
        print("❌ HASHNODE_PUBLICATION_ID not set in .env")
        return
    
    print(f"\n📋 Configuration:")
    print(f"   API Token: {'✓ Set' if HASHNODE_API_TOKEN else '✗ Not set'}")
    print(f"   Publication ID: {HASHNODE_PUBLICATION_ID}")
    
    # Run tests
    tests = [
        ("Authentication", test_authentication),
        ("Get Publications", test_get_publications),
        ("Publish Simple", test_publish_simple),
        ("Publish with Tags", test_publish_with_tags),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"\n❌ Exception in {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    all_pass = all(results.values())
    if all_pass:
        print("\n✅ All tests passed! Hashnode integration should work.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
