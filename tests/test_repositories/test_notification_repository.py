from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.notification import NotificationCreateDTO, NotificationUpdateDTO
from app.schemas.user import UserCreateDTO


class TestNotificationRepository:
    async def test_create_notifications(self, notifications: list[NotificationCreateDTO], users: list[UserCreateDTO], notification_repository: NotificationRepository, user_repository: UserRepository):
        await user_repository.create(users[0])
        notification = await notification_repository.create(notifications[0])

        assert notification.id is not None
        assert notification.user_id == notifications[0].user_id
        assert notification.message == notifications[0].message
        assert notification.is_read == False

    async def test_delete_notification(self, notifications: list[NotificationCreateDTO], users: list[UserCreateDTO], notification_repository: NotificationRepository, user_repository: UserRepository):
        await user_repository.create(users[0])
        notification = await notification_repository.create(notifications[0])
        await notification_repository.delete(notification)

        found_notification = await notification_repository.get_by_id(notification.id)
        assert found_notification is None

    async def test_update_notification(self, notifications: list[NotificationCreateDTO], users: list[UserCreateDTO], notification_repository: NotificationRepository, user_repository: UserRepository):
        await user_repository.create(users[0])
        notification = await notification_repository.create(notifications[0])

        new_notification_data = NotificationUpdateDTO(message="Updated")

        await notification_repository.update(notification, new_notification_data)
        updated_notification = await notification_repository.get_by_id(notification.id)

        assert updated_notification.message == new_notification_data.message

        assert updated_notification.id == notification.id
        assert updated_notification.user_id == notification.user_id
        assert updated_notification.is_read == notification.is_read

    async def test_get_all(self, notifications: list[NotificationCreateDTO], users: list[UserCreateDTO], notification_repository: NotificationRepository, user_repository: UserRepository):
        await user_repository.create(users[0])
        await notification_repository.create(notifications[0])
        await notification_repository.create(notifications[1])

        notifications_list = await notification_repository.get_all()

        notification_messages = [notification.message for notification in notifications_list]

        assert len(notifications_list) == 2
        assert set(notification_messages) == {notifications[0].message, notifications[1].message}
