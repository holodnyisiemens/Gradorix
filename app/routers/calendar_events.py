import datetime
from typing import Optional

from fastapi import APIRouter, Depends

from app.auth.utils import get_current_user
from app.core.enums import CalendarEventType
from app.dependencies import CalendarEventServiceDep, NotificationServiceDep, PushServiceDep
from app.models.user import User
from app.schemas.calendar_event import CalendarEventCreateDTO, CalendarEventReadDTO, CalendarEventUpdateDTO
from app.ws.notify import push_notification

router = APIRouter(prefix="/calendar-events", tags=["Calendar Events"])


def _time_str(t: Optional[datetime.time]) -> str:
    return t.strftime("%H:%M") if t else ""


@router.get("/", response_model=list[CalendarEventReadDTO])
async def get_all(
    date: Optional[datetime.date] = None,
    event_type: Optional[CalendarEventType] = None,
    service: CalendarEventServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_all(date=date, event_type=event_type)


@router.get("/{event_id}", response_model=CalendarEventReadDTO)
async def get_by_id(
    event_id: int,
    service: CalendarEventServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_by_id(event_id)


@router.post("/", response_model=CalendarEventReadDTO, status_code=201)
async def create(
    data: CalendarEventCreateDTO,
    service: CalendarEventServiceDep = ...,
    notification_service: NotificationServiceDep = ...,
    push_service: PushServiceDep = ...,
    current_user: User = Depends(get_current_user),
):
    data.created_by = current_user.id
    event = await service.create(data)

    if event.event_type == CalendarEventType.MEETING and event.attendee_ids:
        time_part = ""
        if event.start_time:
            time_part = f" в {_time_str(event.start_time)}"
            if event.end_time:
                time_part += f"–{_time_str(event.end_time)}"
        msg = f"📅 Новая встреча: «{event.title}» — {event.date}{time_part}"
        link = "/calendar"
        for uid in event.attendee_ids:
            if uid != current_user.id:
                await push_notification(uid, msg, notification_service, push_service, link)

    return event


@router.patch("/{event_id}", response_model=CalendarEventReadDTO)
async def update(
    event_id: int,
    data: CalendarEventUpdateDTO,
    service: CalendarEventServiceDep = ...,
    notification_service: NotificationServiceDep = ...,
    push_service: PushServiceDep = ...,
    current_user: User = Depends(get_current_user),
):
    old = await service.get_by_id(event_id)
    event = await service.update(event_id, data)

    # Notify newly-added attendees only
    if event.event_type == CalendarEventType.MEETING and data.attendee_ids is not None:
        old_ids = set(old.attendee_ids)
        new_ids = set(event.attendee_ids)
        added = new_ids - old_ids
        time_part = ""
        if event.start_time:
            time_part = f" в {_time_str(event.start_time)}"
            if event.end_time:
                time_part += f"–{_time_str(event.end_time)}"
        msg = f"📅 Вас добавили на встречу: «{event.title}» — {event.date}{time_part}"
        for uid in added:
            if uid != current_user.id:
                await push_notification(uid, msg, notification_service, push_service, "/calendar")

    return event


@router.delete("/{event_id}", status_code=204)
async def delete(
    event_id: int,
    service: CalendarEventServiceDep = ...,
    _: User = Depends(get_current_user),
):
    await service.delete(event_id)
