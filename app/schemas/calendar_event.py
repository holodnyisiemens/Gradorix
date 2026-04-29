import datetime
from typing import Annotated, List, Optional

from annotated_types import MaxLen

from app.core.enums import CalendarEventType
from app.schemas.base import BaseDTO


class CalendarEventCreateDTO(BaseDTO):
    title: Annotated[str, MaxLen(255)]
    date: datetime.date
    event_type: CalendarEventType
    challenge_id: Optional[int] = None
    description: Optional[str] = None
    start_time: Optional[datetime.time] = None
    end_time: Optional[datetime.time] = None
    attendee_ids: List[int] = []
    created_by: Optional[int] = None


class CalendarEventReadDTO(BaseDTO):
    id: int
    title: str
    date: datetime.date
    event_type: CalendarEventType
    challenge_id: Optional[int] = None
    description: Optional[str] = None
    start_time: Optional[datetime.time] = None
    end_time: Optional[datetime.time] = None
    attendee_ids: List[int] = []
    created_by: Optional[int] = None


class CalendarEventUpdateDTO(BaseDTO):
    title: Optional[Annotated[str, MaxLen(255)]] = None
    date: Optional[datetime.date] = None
    event_type: Optional[CalendarEventType] = None
    challenge_id: Optional[int] = None
    description: Optional[str] = None
    start_time: Optional[datetime.time] = None
    end_time: Optional[datetime.time] = None
    attendee_ids: Optional[List[int]] = None
