import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.calendar_event import CalendarEvent
from app.repositories.calendar_event_repository import CalendarEventRepository
from app.schemas.calendar_event import CalendarEventCreateDTO, CalendarEventReadDTO, CalendarEventUpdateDTO
from app.core.enums import CalendarEventType


class CalendarEventService:
    def __init__(self, repo: CalendarEventRepository):
        self.repo = repo

    async def _get_or_404(self, event_id: int) -> CalendarEvent:
        event = await self.repo.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"CalendarEvent {event_id} not found")
        return event

    async def get_by_id(self, event_id: int) -> CalendarEventReadDTO:
        return CalendarEventReadDTO.model_validate(await self._get_or_404(event_id))

    async def get_all(
        self,
        date: Optional[datetime.date] = None,
        event_type: Optional[CalendarEventType] = None,
    ) -> list[CalendarEventReadDTO]:
        events = await self.repo.get_all(date=date, event_type=event_type)
        return [CalendarEventReadDTO.model_validate(e) for e in events]

    async def create(self, data: CalendarEventCreateDTO) -> CalendarEventReadDTO:
        try:
            event = await self.repo.create(data)
            await self.repo.session.commit()
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Referenced challenge not found")
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CalendarEvent creation error")
        return CalendarEventReadDTO.model_validate(event)

    async def update(self, event_id: int, data: CalendarEventUpdateDTO) -> CalendarEventReadDTO:
        event = await self._get_or_404(event_id)
        try:
            event = await self.repo.update(event, data)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CalendarEvent update error")
        return CalendarEventReadDTO.model_validate(event)

    async def delete(self, event_id: int) -> None:
        event = await self._get_or_404(event_id)
        try:
            await self.repo.delete(event)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CalendarEvent delete error")
