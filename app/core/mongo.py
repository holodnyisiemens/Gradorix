from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

_client: AsyncIOMotorClient | None = None

MESSAGES_COLLECTION = "mentor_chat_messages"
READ_STATE_COLLECTION = "mentor_chat_read_state"


def get_client() -> AsyncIOMotorClient:
    if _client is None:
        raise RuntimeError("MongoDB client is not initialized")
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_client()[settings.MONGO_DB]


async def init_mongo() -> None:
    global _client
    _client = AsyncIOMotorClient(settings.mongo_url)
    db = _client[settings.MONGO_DB]

    await db[MESSAGES_COLLECTION].create_index(
        [("mentor_id", 1), ("employee_id", 1), ("created_at", -1)],
    )
    await db[READ_STATE_COLLECTION].create_index(
        [("user_id", 1), ("mentor_id", 1), ("employee_id", 1)],
        unique=True,
    )


async def close_mongo() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
