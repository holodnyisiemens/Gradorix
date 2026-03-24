import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calendar_event import CalendarEvent
from app.schemas.calendar_event import CalendarEventCreateDTO, CalendarEventUpdateDTO
from app.core.enums import CalendarEventType


class CalendarEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, event_id: int) -> Optional[CalendarEvent]:
        return await self.session.get(CalendarEvent, event_id)

    async def create(self, data: CalendarEventCreateDTO) -> CalendarEvent:
        event = CalendarEvent(**data.model_dump())
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def delete(self, event: CalendarEvent) -> None:
        await self.session.delete(event)
        await self.session.flush()

    async def update(self, event: CalendarEvent, data: CalendarEventUpdateDTO) -> CalendarEvent:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(event, field, value)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def get_all(
        self,
        date: Optional[datetime.date] = None,
        event_type: Optional[CalendarEventType] = None,
    ) -> list[CalendarEvent]:
        stmt = select(CalendarEvent)
        if date is not None:
            stmt = stmt.where(CalendarEvent.date == date)
        if event_type is not None:
            stmt = stmt.where(CalendarEvent.event_type == event_type)
        result = await self.session.execute(stmt)
        return result.scalars().all()
