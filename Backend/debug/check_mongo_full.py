#!/usr/bin/env python
"""
Comprehensive MongoDB Diagnostics for Blogy AI
Checks: connection, database, collections, indexes, documents, and CRUD operations.
"""

import asyncio
import sys
from datetime import datetime


async def main():
    print("=" * 65)
    print("🔍 Blogy AI — Comprehensive MongoDB Diagnostic")
    print("=" * 65)

    # ── 1. Import checks ──────────────────────────────────────────────
    print("\n[1] Import Checks")
    try:
        import motor.motor_asyncio
        print("   ✅ motor.motor_asyncio imported")
    except ImportError as e:
        print(f"   ❌ motor import failed: {e}")
        return 1

    try:
        from Backend.core.database import connect_to_mongo, disconnect_from_mongo, get_db, get_blogs_collection
        from config import MONGODB_URL, MONGODB_DB_NAME
        print("   ✅ database module imported")
        print(f"   📦 Database name: {MONGODB_DB_NAME}")
        # Mask password in URL for display
        display_url = MONGODB_URL
        if "@" in display_url:
            parts = display_url.split("@")
            display_url = "mongodb+srv://***:***@" + parts[-1]
        print(f"   🔗 MongoDB URL: {display_url}")
    except ImportError as e:
        print(f"   ❌ database module import failed: {e}")
        return 1

    # ── 2. Connection test ────────────────────────────────────────────
    print("\n[2] MongoDB Connection")
    try:
        await connect_to_mongo()
        print("   ✅ Connected successfully")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return 1

    db = get_db()

    # ── 3. List all collections ───────────────────────────────────────
    print("\n[3] Collections in Database")
    try:
        collections = await db.list_collection_names()
        if collections:
            for coll_name in sorted(collections):
                count = await db[coll_name].count_documents({})
                print(f"   📁 {coll_name} — {count} document(s)")
        else:
            print("   ⚠️  No collections exist yet (they'll be created on first write)")
    except Exception as e:
        print(f"   ❌ Failed to list collections: {e}")

    # ── 4. Check indexes on 'blogs' collection ────────────────────────
    print("\n[4] Indexes on 'blogs' Collection")
    try:
        blogs_coll = get_blogs_collection()
        indexes = await blogs_coll.index_information()
        if indexes:
            for idx_name, idx_info in indexes.items():
                keys = idx_info.get("key", [])
                print(f"   🔑 {idx_name}: {keys}")
        else:
            print("   ⚠️  No indexes found")
    except Exception as e:
        print(f"   ❌ Failed to read indexes: {e}")

    # ── 5. Show sample documents in blogs collection ──────────────────
    print("\n[5] Sample Blog Documents")
    try:
        blogs_coll = get_blogs_collection()
        count = await blogs_coll.count_documents({})
        print(f"   📊 Total blog documents: {count}")

        if count > 0:
            cursor = blogs_coll.find().sort("created_at", -1).limit(3)
            docs = await cursor.to_list(length=3)
            for i, doc in enumerate(docs, 1):
                doc_id = str(doc.get("_id", "N/A"))
                keyword = doc.get("keyword", "N/A")
                title = doc.get("title", "N/A")[:60]
                status = doc.get("status", "N/A")
                seo = doc.get("seo_score", "N/A")
                created = doc.get("created_at", "N/A")
                wc = doc.get("word_count", "N/A")
                print(f"\n   --- Blog #{i} ---")
                print(f"   ID       : {doc_id}")
                print(f"   Title    : {title}")
                print(f"   Keyword  : {keyword}")
                print(f"   Status   : {status}")
                print(f"   SEO Score: {seo}")
                print(f"   Words    : {wc}")
                print(f"   Created  : {created}")
        else:
            print("   ⚠️  No blog documents yet — they will appear after /blog/generate is called")
    except Exception as e:
        print(f"   ❌ Failed to query blogs: {e}")

    # ── 6. Test CRUD operations ───────────────────────────────────────
    print("\n[6] CRUD Test (insert → read → delete)")
    try:
        blogs_coll = get_blogs_collection()

        # Insert test document
        test_doc = {
            "keyword": "__test_keyword__",
            "target_word_count": 100,
            "content": "This is a test blog post for MongoDB verification.",
            "title": "Test Blog Post",
            "seo_score": 75,
            "word_count": 10,
            "metadata": {"test": True},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "draft",
        }
        result = await blogs_coll.insert_one(test_doc)
        inserted_id = result.inserted_id
        print(f"   ✅ INSERT: document created with ID = {inserted_id}")

        # Read it back
        found = await blogs_coll.find_one({"_id": inserted_id})
        if found and found.get("keyword") == "__test_keyword__":
            print(f"   ✅ READ  : document retrieved successfully")
        else:
            print(f"   ❌ READ  : document not found or data mismatch")

        # Delete it
        del_result = await blogs_coll.delete_one({"_id": inserted_id})
        if del_result.deleted_count == 1:
            print(f"   ✅ DELETE: test document removed")
        else:
            print(f"   ❌ DELETE: failed to remove test document")

    except Exception as e:
        print(f"   ❌ CRUD test failed: {e}")

    # ── 7. Check blog.py save integration ─────────────────────────────
    print("\n[7] Integration Check — blog.py save-to-MongoDB")
    try:
        import inspect
        import blog as blog_module
        source = inspect.getsource(blog_module.generate_blog)
        checks = {
            "imports get_blogs_collection": "get_blogs_collection" in source,
            "creates BlogDocument": "BlogDocument" in source,
            "calls insert_one": "insert_one" in source,
            "captures blog_id": "blog_id" in source,
        }
        for desc, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {desc}")
    except Exception as e:
        print(f"   ❌ Could not inspect blog.py: {e}")

    # ── 8. Check blog_management.py CRUD routes ───────────────────────
    print("\n[8] Integration Check — blog_management.py routes")
    try:
        import blog_management as bm_module
        routes = [r for r in dir(bm_module) if not r.startswith("_")]
        endpoints = {
            "list_blogs": hasattr(bm_module, "list_blogs"),
            "get_blog": hasattr(bm_module, "get_blog"),
            "delete_blog": hasattr(bm_module, "delete_blog"),
        }
        for name, exists in endpoints.items():
            status = "✅" if exists else "❌"
            print(f"   {status} {name} endpoint exists")
    except Exception as e:
        print(f"   ❌ Could not inspect blog_management.py: {e}")

    # ── Cleanup ───────────────────────────────────────────────────────
    await disconnect_from_mongo()

    print("\n" + "=" * 65)
    print("✅ Diagnostic complete!")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
