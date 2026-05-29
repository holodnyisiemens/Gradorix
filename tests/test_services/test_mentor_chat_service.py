import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.core.enums import UserRole
from app.models.user import User
from app.services.mentor_chat_service import MentorChatService


def _user(user_id: int, role: UserRole) -> User:
    user = MagicMock(spec=User)
    user.id = user_id
    user.role = role
    user.username = f"user{user_id}"
    return user


@pytest.fixture
def mentor_employee_repo():
    return AsyncMock()


@pytest.fixture
def chat_repo():
    return AsyncMock()


@pytest.fixture
def service(mentor_employee_repo, chat_repo):
    return MentorChatService(mentor_employee_repo, chat_repo)


@pytest.mark.asyncio
async def test_resolve_pair_mentor(service):
    user = _user(10, UserRole.MENTOR)
    mentor_id, employee_id = service.resolve_pair_for_user(user, 42)
    assert mentor_id == 10
    assert employee_id == 42


@pytest.mark.asyncio
async def test_resolve_pair_employee(service):
    user = _user(42, UserRole.EMPLOYEE)
    mentor_id, employee_id = service.resolve_pair_for_user(user, 10)
    assert mentor_id == 10
    assert employee_id == 42


@pytest.mark.asyncio
async def test_send_message_requires_pair(service, mentor_employee_repo, chat_repo):
    user = _user(10, UserRole.MENTOR)
    mentor_employee_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.send_message(user, 42, "hello")

    assert exc.value.status_code == 404
    chat_repo.insert_message.assert_not_called()


@pytest.mark.asyncio
async def test_send_message_success(service, mentor_employee_repo, chat_repo):
    user = _user(10, UserRole.MENTOR)
    mentor_employee_repo.get_by_id.return_value = MagicMock()
    chat_repo.insert_message.return_value = {
        "id": "507f1f77bcf86cd799439011",
        "mentor_id": 10,
        "employee_id": 42,
        "sender_id": 10,
        "body": "hello",
        "created_at": datetime.datetime.now(datetime.timezone.utc),
    }

    result = await service.send_message(user, 42, "hello")

    assert result.body == "hello"
    chat_repo.insert_message.assert_awaited_once_with(10, 42, 10, "hello")


@pytest.mark.asyncio
async def test_assert_user_in_pair_forbidden(service, mentor_employee_repo):
    user = _user(99, UserRole.MENTOR)
    mentor_employee_repo.get_by_id.return_value = MagicMock()

    with pytest.raises(HTTPException) as exc:
        await service.assert_user_in_pair(user, 10, 42)

    assert exc.value.status_code == 403
