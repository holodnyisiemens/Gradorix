import datetime
from typing import Annotated, Optional

from annotated_types import MaxLen

from app.core.enums import CalendarEventType, EventStatus
from app.schemas.base import BaseDTO


class CalendarEventCreateDTO(BaseDTO):
    title: Annotated[str, MaxLen(255)]
    date: datetime.date
    event_type: CalendarEventType
    status: EventStatus = EventStatus.SCHEDULED
    challenge_id: Optional[int] = None
    description: Optional[str] = None


class CalendarEventReadDTO(BaseDTO):
    id: int
    title: str
    date: datetime.date
    event_type: CalendarEventType
    status: EventStatus
    activity_id: Optional[int] = None
    description: Optional[str] = None


class CalendarEventUpdateDTO(BaseDTO):
    title: Optional[Annotated[str, MaxLen(255)]] = None
    date: Optional[datetime.date] = None
    event_type: Optional[CalendarEventType] = None
    status: Optional[EventStatus] = None
    challenge_id: Optional[int] = None
    description: Optional[str] = None
