import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.schemas.activity import ActivityCreateDTO, ActivityUpdateDTO
from app.core.enums import ActivityType, CalendarEventType, EventStatus, TaskStatus


class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, activity_id: int) -> Optional[Activity]:
        return await self.session.get(Activity, activity_id)

    async def create(self, data: ActivityCreateDTO) -> Activity:
        activity = Activity(**data.model_dump())
        self.session.add(activity)
        await self.session.flush()
        await self.session.refresh(activity)
        return activity

    async def delete(self, activity: Activity) -> None:
        await self.session.delete(activity)
        await self.session.flush()

    async def update(self, activity: Activity, data: ActivityUpdateDTO) -> Activity:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(activity, field, value)
        await self.session.flush()
        await self.session.refresh(activity)
        return activity

    async def get_all(
        self,
        user_id: Optional[int] = None,
        activity_type: Optional[ActivityType] = None,
        task_status: Optional[TaskStatus] = None,
        event_status: Optional[EventStatus] = None,
        date: Optional[datetime.date] = None,
        event_type: Optional[CalendarEventType] = None,
    ) -> list[Activity]:
        stmt = select(Activity)
        if user_id is not None:
            stmt = stmt.where(Activity.user_id == user_id)
        if activity_type is not None:
            stmt = stmt.where(Activity.activity_type == activity_type)
        if task_status is not None:
            stmt = stmt.where(Activity.task_status == task_status)
        if event_status is not None:
            stmt = stmt.where(Activity.event_status == event_status)
        if date is not None:
            stmt = stmt.where(Activity.date == date)
        if event_type is not None:
            stmt = stmt.where(Activity.event_type == event_type)
        result = await self.session.execute(stmt)
        return result.scalars().all()
