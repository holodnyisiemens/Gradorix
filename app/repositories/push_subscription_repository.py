from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.push_subscription import PushSubscription


class PushSubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_endpoint(self, endpoint: str) -> Optional[PushSubscription]:
        result = await self.session.execute(
            select(PushSubscription).where(PushSubscription.endpoint == endpoint)
        )
        return result.scalar_one_or_none()

    async def upsert(self, user_id: int, endpoint: str, p256dh: str, auth: str) -> PushSubscription:
        existing = await self.get_by_endpoint(endpoint)
        if existing:
            existing.user_id = user_id
            existing.p256dh = p256dh
            existing.auth = auth
            await self.session.flush()
            await self.session.refresh(existing)
            return existing

        sub = PushSubscription(user_id=user_id, endpoint=endpoint, p256dh=p256dh, auth=auth)
        self.session.add(sub)
        await self.session.flush()
        await self.session.refresh(sub)
        return sub

    async def get_by_user_id(self, user_id: int) -> list[PushSubscription]:
        result = await self.session.execute(
            select(PushSubscription).where(PushSubscription.user_id == user_id)
        )
        return list(result.scalars().all())
