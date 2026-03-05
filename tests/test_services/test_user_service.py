import pytest
from fastapi import HTTPException

from app.schemas.user import UserCreateDTO, UserUpdateDTO
from app.services.user_service import UserService


class TestUserService:
    async def test_create(self, users: list[UserCreateDTO], user_service: UserService):
        dto = await user_service.create(users[0])

        assert dto.id is not None
        assert dto.username == users[0].username
        assert dto.email == users[0].email
        assert dto.role == users[0].role

    async def test_create_duplicate_username(self, users: list[UserCreateDTO], user_service: UserService):
        await user_service.create(users[0])

        duplicate = UserCreateDTO(
            username=users[0].username,
            email="other@example.com",
            password="123456",
            role=users[0].role,
        )
        with pytest.raises(HTTPException) as exc_info:
            await user_service.create(duplicate)

        assert exc_info.value.status_code == 409

    async def test_create_duplicate_email(self, users: list[UserCreateDTO], user_service: UserService):
        await user_service.create(users[0])

        duplicate = UserCreateDTO(
            username="otherusername",
            email=users[0].email,
            password="123456",
            role=users[0].role,
        )
        with pytest.raises(HTTPException) as exc_info:
            await user_service.create(duplicate)

        assert exc_info.value.status_code == 409

    async def test_get_by_id(self, users: list[UserCreateDTO], user_service: UserService):
        created = await user_service.create(users[0])

        dto = await user_service.get_by_id(created.id)

        assert dto.id == created.id
        assert dto.username == created.username
        assert dto.email == created.email

    async def test_get_by_id_not_found(self, user_service: UserService):
        with pytest.raises(HTTPException) as exc_info:
            await user_service.get_by_id(999)

        assert exc_info.value.status_code == 404

    async def test_delete(self, users: list[UserCreateDTO], user_service: UserService):
        created = await user_service.create(users[0])

        await user_service.delete(created.id)

        with pytest.raises(HTTPException) as exc_info:
            await user_service.get_by_id(created.id)

        assert exc_info.value.status_code == 404

    async def test_delete_not_found(self, user_service: UserService):
        with pytest.raises(HTTPException) as exc_info:
            await user_service.delete(999)

        assert exc_info.value.status_code == 404

    async def test_update(self, users: list[UserCreateDTO], user_service: UserService):
        created = await user_service.create(users[0])

        update_data = UserUpdateDTO(username="updated_username")
        dto = await user_service.update(created.id, update_data)

        assert dto.username == update_data.username
        assert dto.id == created.id
        assert dto.email == created.email
        assert dto.role == created.role

    async def test_update_not_found(self, user_service: UserService):
        with pytest.raises(HTTPException) as exc_info:
            await user_service.update(999, UserUpdateDTO(username="validname"))

        assert exc_info.value.status_code == 404

    async def test_get_all(self, users: list[UserCreateDTO], user_service: UserService):
        await user_service.create(users[0])
        await user_service.create(users[1])

        result = await user_service.get_all()

        assert len(result) == 2
        usernames = {dto.username for dto in result}
        assert usernames == {users[0].username, users[1].username}
