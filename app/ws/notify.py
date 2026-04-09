from app.schemas.notification import NotificationCreateDTO, NotificationReadDTO
from app.services.notification_service import NotificationService
from app.ws.manager import manager


def _ws_payload(notification: NotificationReadDTO) -> dict:
    return {
        "type": "notification",
        "payload": {
            "id": notification.id,
            "user_id": notification.user_id,
            "title": "",
            "body": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat() if notification.created_at else None,
        },
    }


async def push_ws_only(notification: NotificationReadDTO) -> None:
    """Send an already-saved notification over WebSocket (no DB write)."""
    await manager.send_to_user(notification.user_id, _ws_payload(notification))


async def push_notification(
    user_id: int,
    message: str,
    notification_service: NotificationService,
) -> None:
    """Save a notification to DB and push it over WebSocket if the user is connected."""
    notification = await notification_service.create(
        NotificationCreateDTO(user_id=user_id, message=message)
    )
    await manager.send_to_user(notification.user_id, _ws_payload(notification))
