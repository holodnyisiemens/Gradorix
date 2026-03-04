from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateDTO, UserUpdateDTO


class TestUserRepository:
    async def test_create_user(self, users: list[UserCreateDTO], user_repository: UserRepository):
        user = await user_repository.create(users[0])

        assert user.id is not None
        assert user.username == users[0].username
        assert user.email == users[0].email
        assert user.role == users[0].role

    async def test_delete_user(self, users: list[UserCreateDTO], user_repository: UserRepository):
        user = await user_repository.create(users[0])
        await user_repository.delete(user)

        found_user = await user_repository.get_by_id(user.id)
        assert found_user is None

    async def test_update_user(self, users: list[UserCreateDTO], user_repository: UserRepository):
        user = await user_repository.create(users[0])

        new_user_data = UserUpdateDTO(username="Updated")

        await user_repository.update(user, new_user_data)
        updated_user = await user_repository.get_by_id(user.id)

        assert updated_user.username == new_user_data.username

        assert updated_user.id == user.id
        assert updated_user.email == user.email
        assert updated_user.role == user.role
        assert updated_user.is_active == user.is_active

    async def test_get_all(self, users: list[UserCreateDTO], user_repository: UserRepository):
        await user_repository.create(users[0])
        await user_repository.create(users[1])

        users_list = await user_repository.get_all()

        user_emails = [user.email for user in users_list]

        assert len(users_list) == 2
        assert set(user_emails) == {users[0].email, users[1].email}
