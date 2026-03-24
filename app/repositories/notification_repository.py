from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import NotificationCreateDTO, NotificationUpdateDTO


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        return await self.session.get(Notification, notification_id)

    async def create(self, notification_data: NotificationCreateDTO) -> Notification:
        notification = Notification(**notification_data.model_dump())
        self.session.add(notification)

        await self.session.flush()
        await self.session.refresh(notification)

        return notification

    async def delete(self, notification: Notification) -> None:
        await self.session.delete(notification)
        await self.session.flush()

    async def update(self, notification: Notification, notification_data: NotificationUpdateDTO) -> Notification:
        update_data = notification_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(notification, field, value)

        await self.session.flush()
        await self.session.refresh(notification)

        return notification

    async def get_all(self, user_id: Optional[int] = None) -> list[Notification]:
        stmt = select(Notification)
        if user_id is not None:
            stmt = stmt.where(Notification.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
