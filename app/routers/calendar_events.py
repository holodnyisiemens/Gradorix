import datetime
from typing import Optional

from fastapi import APIRouter

from app.dependencies import CalendarEventServiceDep
from app.schemas.calendar_event import CalendarEventCreateDTO, CalendarEventReadDTO, CalendarEventUpdateDTO
from app.core.enums import CalendarEventType

router = APIRouter(prefix="/calendar-events", tags=["Calendar Events"])


@router.get("/", response_model=list[CalendarEventReadDTO])
async def get_all(
    date: Optional[datetime.date] = None,
    event_type: Optional[CalendarEventType] = None,
    service: CalendarEventServiceDep = ...,
):
    return await service.get_all(date=date, event_type=event_type)


@router.get("/{event_id}", response_model=CalendarEventReadDTO)
async def get_by_id(event_id: int, service: CalendarEventServiceDep = ...):
    return await service.get_by_id(event_id)


@router.post("/", response_model=CalendarEventReadDTO, status_code=201)
async def create(data: CalendarEventCreateDTO, service: CalendarEventServiceDep = ...):
    return await service.create(data)


@router.patch("/{event_id}", response_model=CalendarEventReadDTO)
async def update(event_id: int, data: CalendarEventUpdateDTO, service: CalendarEventServiceDep = ...):
    return await service.update(event_id, data)


@router.delete("/{event_id}", status_code=204)
async def delete(event_id: int, service: CalendarEventServiceDep = ...):
    await service.delete(event_id)
