from typing import Optional

from app.schemas.notification import NotificationCreateDTO, NotificationReadDTO
from app.services.notification_service import NotificationService
from app.services.push_service import PushService
from app.ws.manager import manager


def _ws_payload(notification: NotificationReadDTO) -> dict:
    return {
        "type": "notification",
        "payload": {
            "id": notification.id,
            "user_id": notification.user_id,
            "title": "",
            "body": notification.message,
            "link": notification.link,
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
    push_service: Optional[PushService] = None,
    link: Optional[str] = None,
) -> None:
    """Save a notification to DB, push over WebSocket, and send Web Push if subscribed."""
    notification = await notification_service.create(
        NotificationCreateDTO(user_id=user_id, message=message, link=link)
    )
    await manager.send_to_user(notification.user_id, _ws_payload(notification))
    if push_service:
        await push_service.send(notification)
