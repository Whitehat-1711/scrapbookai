#!/usr/bin/env python
"""
Test MongoDB Connection
Run this to verify Motor and MongoDB are working correctly
"""

import asyncio
import sys

async def test_motor_import():
    """Test that motor imports correctly"""
    try:
        import motor.motor_asyncio
        print("✅ Motor imports successfully")
        print(f"   Motor version: {motor.__version__ if hasattr(motor, '__version__') else 'unknown'}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import motor: {e}")
        return False


async def test_database_import():
    """Test that database module imports correctly"""
    try:
        from backend.core.database import connect_to_mongo, disconnect_from_mongo
        print("✅ Database module imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import database: {e}")
        return False


async def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        from backend.core.database import connect_to_mongo, disconnect_from_mongo
        print("\n🔌 Attempting MongoDB connection...")
        
        await connect_to_mongo()
        print("✅ MongoDB connection successful!")
        
        await disconnect_from_mongo()
        print("✅ MongoDB disconnection successful!")
        
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\n💡 Check your .env file:")
        print("   - MONGODB_URL must be set correctly")
        print("   - For Atlas: mongodb+srv://user:pass@cluster.mongodb.net/")
        print("   - For local: mongodb://localhost:27017")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Blogy AI MongoDB Connection Tests")
    print("=" * 60)
    
    tests = [
        ("Motor Import", test_motor_import),
        ("Database Module Import", test_database_import),
        ("MongoDB Connection", test_mongodb_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        result = await test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} — {test_name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! MongoDB is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Fix errors above and try again.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
