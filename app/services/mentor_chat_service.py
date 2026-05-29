from __future__ import annotations

import datetime
from typing import Optional

from fastapi import HTTPException
from starlette import status

from app.core.enums import UserRole
from app.models.user import User
from app.repositories.mentor_chat_mongo_repository import MentorChatMongoRepository
from app.repositories.mentor_employee_repository import MentorEmployeeRepository
from app.schemas.mentor_chat import (
    MentorChatConversationDTO,
    MentorChatMessageReadDTO,
)


class MentorChatService:
    def __init__(
        self,
        mentor_employee_repo: MentorEmployeeRepository,
        chat_repo: MentorChatMongoRepository,
    ) -> None:
        self._mentor_employee_repo = mentor_employee_repo
        self._chat_repo = chat_repo

    async def assert_pair_exists(self, mentor_id: int, employee_id: int) -> None:
        pair = await self._mentor_employee_repo.get_by_id(mentor_id, employee_id)
        if not pair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mentor-employee pair not found",
            )

    def resolve_pair_for_user(self, user: User, peer_id: int) -> tuple[int, int]:
        if user.role == UserRole.MENTOR:
            return user.id, peer_id
        if user.role == UserRole.EMPLOYEE:
            return peer_id, user.id
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chat is only available for mentors and employees",
        )

    async def assert_user_in_pair(
        self,
        user: User,
        mentor_id: int,
        employee_id: int,
    ) -> None:
        await self.assert_pair_exists(mentor_id, employee_id)
        if user.role == UserRole.MENTOR and user.id != mentor_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        if user.role == UserRole.EMPLOYEE and user.id != employee_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        if user.role not in (UserRole.MENTOR, UserRole.EMPLOYEE):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    def _peer_id_for_user(self, user: User, mentor_id: int, employee_id: int) -> int:
        if user.role == UserRole.MENTOR:
            return employee_id
        return mentor_id

    async def get_conversations(self, user: User) -> list[MentorChatConversationDTO]:
        if user.role == UserRole.MENTOR:
            pairs = await self._mentor_employee_repo.get_all(mentor_id=user.id)
        elif user.role == UserRole.EMPLOYEE:
            pairs = await self._mentor_employee_repo.get_all(employee_id=user.id)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        conversations: list[MentorChatConversationDTO] = []
        for pair in pairs:
            mentor_id = pair.mentor_id
            employee_id = pair.employee_id
            last_message = await self._chat_repo.get_last_message(mentor_id, employee_id)
            unread_count = await self._chat_repo.count_unread(
                user.id, mentor_id, employee_id
            )
            last_dto = (
                MentorChatMessageReadDTO.model_validate(last_message)
                if last_message
                else None
            )
            conversations.append(
                MentorChatConversationDTO(
                    mentor_id=mentor_id,
                    employee_id=employee_id,
                    peer_id=self._peer_id_for_user(user, mentor_id, employee_id),
                    last_message=last_dto,
                    unread_count=unread_count,
                )
            )

        epoch = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
        conversations.sort(
            key=lambda c: c.last_message.created_at if c.last_message else epoch,
            reverse=True,
        )
        return conversations

    async def list_messages(
        self,
        user: User,
        mentor_id: int,
        employee_id: int,
        *,
        limit: int = 50,
        before_id: Optional[str] = None,
    ) -> list[MentorChatMessageReadDTO]:
        await self.assert_user_in_pair(user, mentor_id, employee_id)
        docs = await self._chat_repo.list_messages(
            mentor_id,
            employee_id,
            limit=limit,
            before_id=before_id,
        )
        return [MentorChatMessageReadDTO.model_validate(d) for d in docs]

    async def mark_read(
        self,
        user: User,
        mentor_id: int,
        employee_id: int,
    ) -> None:
        await self.assert_user_in_pair(user, mentor_id, employee_id)
        await self._chat_repo.mark_read(user.id, mentor_id, employee_id)

    async def send_message(
        self,
        user: User,
        peer_id: int,
        text: str,
    ) -> MentorChatMessageReadDTO:
        mentor_id, employee_id = self.resolve_pair_for_user(user, peer_id)
        await self.assert_pair_exists(mentor_id, employee_id)
        body = text.strip()
        if not body:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty message",
            )
        doc = await self._chat_repo.insert_message(
            mentor_id, employee_id, user.id, body
        )
        return MentorChatMessageReadDTO.model_validate(doc)

    def recipient_id(self, user: User, mentor_id: int, employee_id: int) -> int:
        if user.id == mentor_id:
            return employee_id
        return mentor_id
