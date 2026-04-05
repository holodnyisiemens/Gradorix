import datetime
from typing import Optional

from fastapi import HTTPException
from starlette import status

from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_points_repository import UserPointsRepository
from app.schemas.activity import ActivityCreateDTO, ActivityUpdateDTO
from app.schemas.calendar_event import CalendarEventCreateDTO, CalendarEventReadDTO, CalendarEventUpdateDTO
from app.services.activity_service import ActivityService
from app.core.enums import ActivityType, CalendarEventType, EventStatus


class CalendarEventService:
    def __init__(self, activity_repo: ActivityRepository, points_repo: UserPointsRepository):
        self.activity_service = ActivityService(activity_repo, points_repo)

    async def _get_or_404(self, event_id: int):
        event = await self.activity_service.repo.get_by_id(event_id)
        if not event or event.activity_type != ActivityType.EVENT:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"CalendarEvent {event_id} not found")
        return event

    def _to_calendar_event(self, activity) -> CalendarEventReadDTO:
        return CalendarEventReadDTO(
            id=activity.id,
            title=activity.title,
            date=activity.date,
            event_type=activity.event_type,
            status=activity.event_status,
            activity_id=activity.id,
            description=activity.description,
        )

    async def get_by_id(self, event_id: int) -> CalendarEventReadDTO:
        event = await self._get_or_404(event_id)
        return self._to_calendar_event(event)

    async def get_all(
        self,
        date: Optional[datetime.date] = None,
        event_type: Optional[CalendarEventType] = None,
        status: Optional[EventStatus] = None,
    ) -> list[CalendarEventReadDTO]:
        activities = await self.activity_service.repo.get_all(
            activity_type=ActivityType.EVENT,
            date=date,
            event_type=event_type,
            event_status=status,
        )
        return [self._to_calendar_event(activity) for activity in activities]

    async def create(self, data: CalendarEventCreateDTO) -> CalendarEventReadDTO:
        activity_data = ActivityCreateDTO(
            title=data.title,
            description=data.description or "",
            activity_type=ActivityType.EVENT,
            event_status=data.status,
            date=data.date,
            event_type=data.event_type,
            challenge_id=data.challenge_id,
        )
        activity = await self.activity_service.create(activity_data)
        return self._to_calendar_event(activity)

    async def update(self, event_id: int, data: CalendarEventUpdateDTO) -> CalendarEventReadDTO:
        update_payload = data.model_dump(exclude_unset=True)
        if "status" in update_payload:
            update_payload["event_status"] = update_payload.pop("status")

        activity_data = ActivityUpdateDTO(**update_payload, activity_type=ActivityType.EVENT)
        activity = await self.activity_service.update(event_id, activity_data)
        return self._to_calendar_event(activity)

    async def delete(self, event_id: int) -> None:
        await self.activity_service.delete(event_id)
