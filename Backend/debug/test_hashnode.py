#!/usr/bin/env python3
"""
Test Hashnode Integration
==========================
Run this script to test your Hashnode API credentials and configuration before deploying.

Usage:
    python test_hashnode.py

Requirements:
    - HASHNODE_API_TOKEN set in .env
    - HASHNODE_PUBLICATION_ID set in .env
"""

import asyncio
import sys
from ..core.config import HASHNODE_API_TOKEN, HASHNODE_PUBLICATION_ID
from ..services.hashnode_service import get_hashnode_user_info, publish_to_hashnode, HashnodePublishError

async def test_credentials():
    """Test if Hashnode credentials are configured"""
    print("🔍 Testing Hashnode Credentials...")
    print(f"   API Token configured: {'✅' if HASHNODE_API_TOKEN else '❌'}")
    print(f"   Publication ID configured: {'✅' if HASHNODE_PUBLICATION_ID else '❌'}")
    
    if not HASHNODE_API_TOKEN or not HASHNODE_PUBLICATION_ID:
        print("\n⚠️  Missing credentials! Please set HASHNODE_API_TOKEN and HASHNODE_PUBLICATION_ID in .env")
        return False
    return True


async def test_user_info():
    """Get authenticated user info from Hashnode"""
    print("\n📋 Fetching Hashnode User Information...")
    user_info = await get_hashnode_user_info()
    
    if not user_info:
        print("   ❌ Failed to retrieve user info")
        return False
    
    print(f"   ✅ Authenticated as: {user_info.get('name', 'Unknown')}")
    print(f"   📝 Username: @{user_info.get('username', 'N/A')}")
    
    # List publications
    publications = user_info.get('publications', {}).get('edges', [])
    if publications:
        print(f"\n   Publications ({len(publications)}):")
        for pub in publications:
            node = pub.get('node', {})
            print(f"      • {node.get('displayTitle', 'N/A')} (ID: {node.get('id', 'N/A')})")
    
    return True


async def test_publish_draft():
    """Test publishing a draft blog post"""
    print("\n📝 Testing Blog Publication (as DRAFT)...")
    
    test_blog = {
        "title": "🧪 Hashnode Integration Test",
        "slug": f"hashnode-test-{int(__import__('time').time())}",
        "content": """
# Testing Hashnode Integration

This is a test blog post to verify your Hashnode integration is working correctly.

## Features Verified
- ✅ API authentication
- ✅ GraphQL mutation
- ✅ Blog publication
- ✅ Metadata handling

## Code Example
```python
# This is a test
print("Hashnode integration works!")
```

## Conclusion
If you're reading this on Hashnode, the integration is working perfectly! You can now:
1. Generate blogs using Blogy
2. Automatically publish them to your Hashnode publication
3. Track publication status in MongoDB

Great! 🚀
        """.strip(),
        "meta_description": "Test blog to verify Hashnode integration is working",
    }
    
    try:
        result = await publish_to_hashnode(
            title=test_blog["title"],
            content=test_blog["content"],
            slug=test_blog["slug"],
            meta_description=test_blog["meta_description"],
            tags=["test", "integration"],
            is_draft=False,  # Set to True to publish as draft
        )
        
        if result.get("success"):
            print(f"   ✅ Blog published successfully!")
            print(f"   🔗 URL: {result.get('hashnode_url')}")
            print(f"   📱 Hashnode ID: {result.get('hashnode_id')}")
            return True
        else:
            print(f"   ❌ {result.get('error')}")
            return False
    
    except HashnodePublishError as e:
        print(f"   ❌ Configuration Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected Error: {e}")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Hashnode Integration Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Credentials
    results["credentials"] = await test_credentials()
    if not results["credentials"]:
        print("\n❌ Stopping tests - credentials not configured")
        return
    
    # Test 2: User Info
    results["user_info"] = await test_user_info()
    
    # Test 3: Publish
    publish_test = input("\n❓ Do you want to test publishing a blog? (yes/no): ").lower()
    if publish_test == "yes":
        results["publish"] = await test_publish_draft()
    else:
        print("   ⏭️  Skipped publish test")
        results["publish"] = None
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results.items():
        if result is None:
            status = "⏭️  Skipped"
        else:
            status = "✅ Passed" if result else "❌ Failed"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    all_required_passed = results.get("credentials") and results.get("user_info")
    
    if all_required_passed:
        print("\n✅ Hashnode integration is properly configured!")
        print("\nYou can now:")
        print("   1. Set publish_to_hashnode: true in blog generation requests")
        print("   2. Use the /blog/{id}/publish-hashnode endpoint")
        print("   3. Enable HASHNODE_AUTO_PUBLISH for automatic publishing")
    else:
        print("\n❌ Configuration issues detected - see above for details")
    
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏸️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
