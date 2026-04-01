"""
MongoDB Connection Manager
===========================
Async MongoDB client using Motor (async driver for PyMongo)
"""

import motor.motor_asyncio
from .config import MONGODB_URL, MONGODB_DB_NAME
import logging

logger = logging.getLogger("blogy.db")

# ── Global client reference ───────────────────────────────────────────────────
_client = None
_db = None


async def connect_to_mongo():
    """Initialize MongoDB connection on app startup"""
    global _client, _db

    try:
        _client = motor.motor_asyncio.AsyncIOMotorClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000,  # 🔥 fail fast
        )

        _db = _client[MONGODB_DB_NAME]

        # Test connection
        await _db.command("ping")

        logger.info(f"✅ Connected to MongoDB")
        logger.info(f"📦 Database: {MONGODB_DB_NAME}")

        # Create indexes
        await _create_indexes()

    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")

        # 🔥 CRITICAL FIX: DO NOT CRASH APP
        _client = None
        _db = None

        logger.warning("⚠️ Running WITHOUT MongoDB (non-blocking mode)")


async def disconnect_from_mongo():
    """Close MongoDB connection on app shutdown"""
    global _client
    if _client is not None:
        _client.close()
        logger.info("🔌 Disconnected from MongoDB")


async def _create_indexes():
    """Create database indexes for performance"""
    if _db is None:
        return

    try:
        blogs_collection = _db["blogs"]
        await blogs_collection.create_index("keyword")
        await blogs_collection.create_index("user_id")
        await blogs_collection.create_index("created_at")

        logger.info("📑 Database indexes created")

    except Exception as e:
        logger.warning(f"⚠️ Index creation failed: {e}")


def get_db():
    """Get database instance (safe version)"""
    if _db is None:
        return None  # 🔥 return None instead of crashing
    return _db


def get_blogs_collection():
    """Get blogs collection safely"""
    db = get_db()
    if db is None:
        return None
    return db["blogs"]


def get_users_collection():
    """Get users collection safely"""
    db = get_db()
    if db is None:
        return None
    return db["users"]