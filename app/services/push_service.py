import asyncio
import json
import logging

from pywebpush import webpush, WebPushException

from app.core.config import settings
from app.repositories.push_subscription_repository import PushSubscriptionRepository
from app.schemas.notification import NotificationReadDTO
from app.schemas.push import PushSubscribeDTO

logger = logging.getLogger(__name__)


class PushService:
    def __init__(self, repo: PushSubscriptionRepository):
        self.repo = repo

    async def subscribe(self, data: PushSubscribeDTO, user_id: int) -> None:
        keys = data.subscription.keys
        await self.repo.upsert(
            user_id=user_id,
            endpoint=data.subscription.endpoint,
            p256dh=keys.p256dh,
            auth=keys.auth,
        )
        await self.repo.session.commit()

    async def send(self, notification: NotificationReadDTO) -> None:
        if not settings.VAPID_PRIVATE_KEY:
            return

        subscriptions = await self.repo.get_by_user_id(notification.user_id)
        if not subscriptions:
            return

        payload = json.dumps({
            "title": "Gradorix",
            "body": notification.message,
            "link": notification.link or "/notifications",
        })

        for sub in subscriptions:
            try:
                await asyncio.to_thread(
                    webpush,
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                    },
                    data=payload,
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": f"mailto:{settings.VAPID_SUBSCRIBER}"},
                    content_encoding="aes128gcm",
                )
            except WebPushException as exc:
                status_code = exc.response.status_code if exc.response else None
                if status_code in (404, 410):
                    await self.repo.session.delete(sub)
                    await self.repo.session.commit()
                else:
                    logger.warning("Push failed for sub %s: %s", sub.id, exc)
            except Exception as exc:
                logger.warning("Push failed for sub %s: %s", sub.id, exc)
