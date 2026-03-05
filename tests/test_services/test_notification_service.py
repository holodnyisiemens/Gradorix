import pytest
from fastapi import HTTPException

from app.repositories.user_repository import UserRepository
from app.schemas.notification import NotificationCreateDTO, NotificationUpdateDTO
from app.schemas.user import UserCreateDTO
from app.services.notification_service import NotificationService


class TestNotificationService:
    async def test_create(
        self,
        users: list[UserCreateDTO],
        notifications: list[NotificationCreateDTO],
        user_repository: UserRepository,
        notification_service: NotificationService,
    ):
        user = await user_repository.create(users[0])

        data = NotificationCreateDTO(user_id=user.id, message=notifications[0].message)
        dto = await notification_service.create(data)

        assert dto.id is not None
        assert dto.user_id == user.id
        assert dto.message == notifications[0].message
        assert dto.is_read is False

    async def test_get_by_id(
        self,
        users: list[UserCreateDTO],
        notifications: list[NotificationCreateDTO],
        user_repository: UserRepository,
        notification_service: NotificationService,
    ):
        user = await user_repository.create(users[0])

        created = await notification_service.create(
            NotificationCreateDTO(user_id=user.id, message=notifications[0].message)
        )

        dto = await notification_service.get_by_id(created.id)

        assert dto.id == created.id
        assert dto.user_id == created.user_id
        assert dto.message == created.message

    async def test_get_by_id_not_found(self, notification_service: NotificationService):
        with pytest.raises(HTTPException) as exc_info:
            await notification_service.get_by_id(999)

        assert exc_info.value.status_code == 404

    async def test_delete(
        self,
        users: list[UserCreateDTO],
        notifications: list[NotificationCreateDTO],
        user_repository: UserRepository,
        notification_service: NotificationService,
    ):
        user = await user_repository.create(users[0])
        created = await notification_service.create(
            NotificationCreateDTO(user_id=user.id, message=notifications[0].message)
        )

        await notification_service.delete(created.id)

        with pytest.raises(HTTPException) as exc_info:
            await notification_service.get_by_id(created.id)

        assert exc_info.value.status_code == 404

    async def test_delete_not_found(self, notification_service: NotificationService):
        with pytest.raises(HTTPException) as exc_info:
            await notification_service.delete(999)

        assert exc_info.value.status_code == 404

    async def test_update(
        self,
        users: list[UserCreateDTO],
        notifications: list[NotificationCreateDTO],
        user_repository: UserRepository,
        notification_service: NotificationService,
    ):
        user = await user_repository.create(users[0])
        created = await notification_service.create(
            NotificationCreateDTO(user_id=user.id, message=notifications[0].message)
        )

        update_data = NotificationUpdateDTO(message="Updated message", is_read=True)
        dto = await notification_service.update(created.id, update_data)

        assert dto.message == update_data.message
        assert dto.is_read is True
        assert dto.id == created.id
        assert dto.user_id == created.user_id

    async def test_update_not_found(self, notification_service: NotificationService):
        with pytest.raises(HTTPException) as exc_info:
            await notification_service.update(999, NotificationUpdateDTO(message="x"))

        assert exc_info.value.status_code == 404

    async def test_get_all(
        self,
        users: list[UserCreateDTO],
        notifications: list[NotificationCreateDTO],
        user_repository: UserRepository,
        notification_service: NotificationService,
    ):
        user = await user_repository.create(users[0])

        await notification_service.create(
            NotificationCreateDTO(user_id=user.id, message=notifications[0].message)
        )
        await notification_service.create(
            NotificationCreateDTO(user_id=user.id, message=notifications[1].message)
        )

        result = await notification_service.get_all()

        assert len(result) == 2
        messages = {dto.message for dto in result}
        assert messages == {notifications[0].message, notifications[1].message}
