import pytest
from fastapi import HTTPException

from app.schemas.user import UserCreateDTO
from app.services.mentor_service import MentorService
from app.services.user_service import UserService


class TestMentorService:
    async def test_get_by_id(self, mentor_users: list[UserCreateDTO], user_service: UserService, mentor_service: MentorService):
        created = await user_service.create(mentor_users[0])

        dto = await mentor_service.get_by_id(created.id)

        assert dto.id == created.id
        assert dto.username == created.username

    async def test_get_by_id_not_mentor(self, users: list[UserCreateDTO], user_service: UserService, mentor_service: MentorService):
        created = await user_service.create(users[0])  # HR role

        with pytest.raises(HTTPException) as exc_info:
            await mentor_service.get_by_id(created.id)

        assert exc_info.value.status_code == 404

    async def test_get_by_id_not_found(self, mentor_service: MentorService):
        with pytest.raises(HTTPException) as exc_info:
            await mentor_service.get_by_id(999)

        assert exc_info.value.status_code == 404

    async def test_get_all_returns_only_mentors(
        self,
        users: list[UserCreateDTO],
        mentor_users: list[UserCreateDTO],
        user_service: UserService,
        mentor_service: MentorService,
    ):
        await user_service.create(users[0])       # HR
        await user_service.create(users[1])       # JUNIOR
        await user_service.create(mentor_users[0])  # MENTOR
        await user_service.create(mentor_users[1])  # MENTOR

        result = await mentor_service.get_all()

        assert len(result) == 2
        usernames = {dto.username for dto in result}
        assert usernames == {mentor_users[0].username, mentor_users[1].username}

    async def test_get_all_empty(self, mentor_service: MentorService):
        result = await mentor_service.get_all()

        assert result == []
