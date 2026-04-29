import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calendar_event import CalendarEvent, CalendarEventAttendee
from app.schemas.calendar_event import CalendarEventCreateDTO, CalendarEventUpdateDTO
from app.core.enums import CalendarEventType


class CalendarEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, event_id: int) -> Optional[CalendarEvent]:
        return await self.session.get(CalendarEvent, event_id)

    async def create(self, data: CalendarEventCreateDTO) -> CalendarEvent:
        payload = data.model_dump(exclude={"attendee_ids"})
        event = CalendarEvent(**payload)
        self.session.add(event)
        await self.session.flush()
        for uid in data.attendee_ids:
            self.session.add(CalendarEventAttendee(event_id=event.id, user_id=uid))
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def delete(self, event: CalendarEvent) -> None:
        await self.session.delete(event)
        await self.session.flush()

    async def update(self, event: CalendarEvent, data: CalendarEventUpdateDTO) -> CalendarEvent:
        dump = data.model_dump(exclude_unset=True, exclude={"attendee_ids"})
        for field, value in dump.items():
            setattr(event, field, value)
        if data.attendee_ids is not None:
            # Replace attendees list
            stmt = select(CalendarEventAttendee).where(CalendarEventAttendee.event_id == event.id)
            result = await self.session.execute(stmt)
            for existing in result.scalars().all():
                await self.session.delete(existing)
            await self.session.flush()
            for uid in data.attendee_ids:
                self.session.add(CalendarEventAttendee(event_id=event.id, user_id=uid))
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
