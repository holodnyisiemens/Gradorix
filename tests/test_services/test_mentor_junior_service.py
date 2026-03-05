import pytest
from fastapi import HTTPException

from app.core.enums import UserRole
from app.schemas.mentor_junior import MentorJuniorCreateDTO, MentorJuniorUpdateDTO
from app.schemas.user import UserCreateDTO
from app.services.mentor_junior_service import MentorJuniorService
from app.repositories.user_repository import UserRepository


def _make_users() -> tuple[UserCreateDTO, UserCreateDTO, UserCreateDTO]:
    hr = UserCreateDTO(username="hr1", email="hr1@example.com", password="123456", role=UserRole.HR)
    mentor = UserCreateDTO(username="mentor1", email="mentor1@example.com", password="123456", role=UserRole.MENTOR)
    junior = UserCreateDTO(username="junior1", email="junior1@example.com", password="123456", role=UserRole.JUNIOR)
    return hr, mentor, junior


class TestMentorJuniorService:
    async def _setup_users(self, user_repository: UserRepository):
        hr, mentor, junior = _make_users()
        hr_user = await user_repository.create(hr)
        mentor_user = await user_repository.create(mentor)
        junior_user = await user_repository.create(junior)
        return hr_user, mentor_user, junior_user

    async def test_create(self, user_repository: UserRepository, mentor_junior_service: MentorJuniorService):
        hr, mentor, junior = await self._setup_users(user_repository)

        data = MentorJuniorCreateDTO(mentor_id=mentor.id, junior_id=junior.id, assigned_by=hr.id)
        dto = await mentor_junior_service.create(data)

        assert dto.mentor_id == mentor.id
        assert dto.junior_id == junior.id
        assert dto.assigned_by == hr.id

    async def test_create_duplicate(self, user_repository: UserRepository, mentor_junior_service: MentorJuniorService):
        hr, mentor, junior = await self._setup_users(user_repository)

        data = MentorJuniorCreateDTO(mentor_id=mentor.id, junior_id=junior.id, assigned_by=hr.id)
        await mentor_junior_service.create(data)

        with pytest.raises(HTTPException) as exc_info:
            await mentor_junior_service.create(data)

        assert exc_info.value.status_code == 409

    async def test_get_by_id(self, user_repository: UserRepository, mentor_junior_service: MentorJuniorService):
        hr, mentor, junior = await self._setup_users(user_repository)

        data = MentorJuniorCreateDTO(mentor_id=mentor.id, junior_id=junior.id, assigned_by=hr.id)
        await mentor_junior_service.create(data)

        dto = await mentor_junior_service.get_by_id(mentor.id, junior.id)

        assert dto.mentor_id == mentor.id
        assert dto.junior_id == junior.id

    async def test_get_by_id_not_found(self, mentor_junior_service: MentorJuniorService):
        with pytest.raises(HTTPException) as exc_info:
            await mentor_junior_service.get_by_id(999, 999)

        assert exc_info.value.status_code == 404

    async def test_delete(self, user_repository: UserRepository, mentor_junior_service: MentorJuniorService):
        hr, mentor, junior = await self._setup_users(user_repository)

        data = MentorJuniorCreateDTO(mentor_id=mentor.id, junior_id=junior.id, assigned_by=hr.id)
        await mentor_junior_service.create(data)

        await mentor_junior_service.delete(mentor.id, junior.id)

        with pytest.raises(HTTPException) as exc_info:
            await mentor_junior_service.get_by_id(mentor.id, junior.id)

        assert exc_info.value.status_code == 404

    async def test_delete_not_found(self, mentor_junior_service: MentorJuniorService):
        with pytest.raises(HTTPException) as exc_info:
            await mentor_junior_service.delete(999, 999)

        assert exc_info.value.status_code == 404

    async def test_update(self, user_repository: UserRepository, mentor_junior_service: MentorJuniorService):
        hr, mentor, junior = await self._setup_users(user_repository)
        second_junior = await user_repository.create(
            UserCreateDTO(username="junior2", email="junior2@example.com", password="123456", role=UserRole.JUNIOR)
        )

        data = MentorJuniorCreateDTO(mentor_id=mentor.id, junior_id=junior.id, assigned_by=hr.id)
        await mentor_junior_service.create(data)

        update_data = MentorJuniorUpdateDTO(assigned_by=second_junior.id)
        dto = await mentor_junior_service.update(mentor.id, junior.id, update_data)

        assert dto.assigned_by == second_junior.id
        assert dto.mentor_id == mentor.id
        assert dto.junior_id == junior.id

    async def test_update_not_found(self, mentor_junior_service: MentorJuniorService):
        with pytest.raises(HTTPException) as exc_info:
            await mentor_junior_service.update(999, 999, MentorJuniorUpdateDTO(assigned_by=1))

        assert exc_info.value.status_code == 404

    async def test_get_all(self, user_repository: UserRepository, mentor_junior_service: MentorJuniorService):
        hr, mentor, junior = await self._setup_users(user_repository)
        second_junior = await user_repository.create(
            UserCreateDTO(username="junior2", email="junior2@example.com", password="123456", role=UserRole.JUNIOR)
        )

        await mentor_junior_service.create(
            MentorJuniorCreateDTO(mentor_id=mentor.id, junior_id=junior.id, assigned_by=hr.id)
        )
        await mentor_junior_service.create(
            MentorJuniorCreateDTO(mentor_id=mentor.id, junior_id=second_junior.id, assigned_by=hr.id)
        )

        result = await mentor_junior_service.get_all()

        assert len(result) == 2
        junior_ids = {dto.junior_id for dto in result}
        assert junior_ids == {junior.id, second_junior.id}
