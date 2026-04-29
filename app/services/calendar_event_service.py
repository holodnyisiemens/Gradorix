import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.calendar_event import CalendarEvent
from app.repositories.calendar_event_repository import CalendarEventRepository
from app.schemas.calendar_event import CalendarEventCreateDTO, CalendarEventReadDTO, CalendarEventUpdateDTO
from app.core.enums import CalendarEventType


def _to_dto(event: CalendarEvent) -> CalendarEventReadDTO:
    return CalendarEventReadDTO(
        id=event.id,
        title=event.title,
        date=event.date,
        event_type=event.event_type,
        challenge_id=event.challenge_id,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        attendee_ids=[a.user_id for a in event.attendees],
        created_by=event.created_by,
    )


class CalendarEventService:
    def __init__(self, repo: CalendarEventRepository):
        self.repo = repo

    async def _get_or_404(self, event_id: int) -> CalendarEvent:
        event = await self.repo.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"CalendarEvent {event_id} not found")
        return event

    async def get_by_id(self, event_id: int) -> CalendarEventReadDTO:
        return _to_dto(await self._get_or_404(event_id))

    async def get_all(
        self,
        date: Optional[datetime.date] = None,
        event_type: Optional[CalendarEventType] = None,
    ) -> list[CalendarEventReadDTO]:
        events = await self.repo.get_all(date=date, event_type=event_type)
        return [_to_dto(e) for e in events]

    async def create(self, data: CalendarEventCreateDTO) -> CalendarEventReadDTO:
        try:
            event = await self.repo.create(data)
            await self.repo.session.commit()
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Referenced entity not found")
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CalendarEvent creation error")
        return _to_dto(event)

    async def update(self, event_id: int, data: CalendarEventUpdateDTO) -> CalendarEventReadDTO:
        event = await self._get_or_404(event_id)
        try:
            event = await self.repo.update(event, data)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CalendarEvent update error")
        return _to_dto(event)

    async def delete(self, event_id: int) -> None:
        event = await self._get_or_404(event_id)
        try:
            await self.repo.delete(event)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CalendarEvent delete error")
