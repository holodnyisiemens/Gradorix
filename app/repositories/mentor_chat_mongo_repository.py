from __future__ import annotations

import datetime
from typing import Any, Optional

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.mongo import MESSAGES_COLLECTION, READ_STATE_COLLECTION


class MentorChatMongoRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._messages = db[MESSAGES_COLLECTION]
        self._read_state = db[READ_STATE_COLLECTION]

    @staticmethod
    def _doc_to_dict(doc: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(doc["_id"]),
            "mentor_id": doc["mentor_id"],
            "employee_id": doc["employee_id"],
            "sender_id": doc["sender_id"],
            "body": doc["body"],
            "created_at": doc["created_at"],
        }

    async def insert_message(
        self,
        mentor_id: int,
        employee_id: int,
        sender_id: int,
        body: str,
    ) -> dict[str, Any]:
        doc = {
            "mentor_id": mentor_id,
            "employee_id": employee_id,
            "sender_id": sender_id,
            "body": body,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        }
        result = await self._messages.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self._doc_to_dict(doc)

    async def list_messages(
        self,
        mentor_id: int,
        employee_id: int,
        *,
        limit: int = 50,
        before_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {
            "mentor_id": mentor_id,
            "employee_id": employee_id,
        }
        if before_id:
            try:
                query["_id"] = {"$lt": ObjectId(before_id)}
            except InvalidId:
                return []

        cursor = self._messages.find(query).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_dict(doc) for doc in reversed(docs)]

    async def get_last_message(
        self,
        mentor_id: int,
        employee_id: int,
    ) -> Optional[dict[str, Any]]:
        doc = await self._messages.find_one(
            {"mentor_id": mentor_id, "employee_id": employee_id},
            sort=[("created_at", -1)],
        )
        if not doc:
            return None
        return self._doc_to_dict(doc)

    async def get_last_read_at(
        self,
        user_id: int,
        mentor_id: int,
        employee_id: int,
    ) -> Optional[datetime.datetime]:
        doc = await self._read_state.find_one(
            {
                "user_id": user_id,
                "mentor_id": mentor_id,
                "employee_id": employee_id,
            }
        )
        if not doc:
            return None
        return doc.get("last_read_at")

    async def mark_read(
        self,
        user_id: int,
        mentor_id: int,
        employee_id: int,
    ) -> datetime.datetime:
        now = datetime.datetime.now(datetime.timezone.utc)
        await self._read_state.update_one(
            {
                "user_id": user_id,
                "mentor_id": mentor_id,
                "employee_id": employee_id,
            },
            {"$set": {"last_read_at": now}},
            upsert=True,
        )
        return now

    async def count_unread(
        self,
        user_id: int,
        mentor_id: int,
        employee_id: int,
    ) -> int:
        query: dict[str, Any] = {
            "mentor_id": mentor_id,
            "employee_id": employee_id,
            "sender_id": {"$ne": user_id},
        }
        last_read = await self.get_last_read_at(user_id, mentor_id, employee_id)
        if last_read is not None:
            query["created_at"] = {"$gt": last_read}
        return await self._messages.count_documents(query)
