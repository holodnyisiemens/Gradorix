import datetime
from typing import Annotated, Optional

from annotated_types import MaxLen
from pydantic import AnyUrl

from app.core.enums import ActivityType, CalendarEventType, EventStatus, TaskStatus
from app.schemas.base import BaseDTO


class ActivityCreateDTO(BaseDTO):
    user_id: Optional[int] = None
    title: Annotated[str, MaxLen(255)]
    description: Annotated[str, MaxLen(1000)]
    requested_points: int = 0
    awarded_points: Optional[int] = None
    activity_type: ActivityType
    task_status: Optional[TaskStatus] = None
    event_status: Optional[EventStatus] = None
    date: Optional[datetime.date] = None
    url: Optional[Annotated[AnyUrl, MaxLen(500)]] = None
    event_type: Optional[CalendarEventType] = None
    challenge_id: Optional[int] = None
    reviewed_at: Optional[datetime.datetime] = None
    review_note: Optional[Annotated[str, MaxLen(1000)]] = None


class ActivityReadDTO(BaseDTO):
    id: int
    user_id: Optional[int] = None
    title: str
    description: str
    requested_points: int
    awarded_points: Optional[int] = None
    task_status: Optional[TaskStatus] = None
    event_status: Optional[EventStatus] = None
    activity_type: ActivityType
    date: Optional[datetime.date] = None
    url: Optional[AnyUrl] = None
    event_type: Optional[CalendarEventType] = None
    challenge_id: Optional[int] = None
    submitted_at: datetime.datetime
    reviewed_at: Optional[datetime.datetime] = None
    review_note: Optional[str] = None


class ActivityUpdateDTO(BaseDTO):
    user_id: Optional[int] = None
    title: Optional[Annotated[str, MaxLen(255)]] = None
    description: Optional[Annotated[str, MaxLen(1000)]] = None
    requested_points: Optional[int] = None
    awarded_points: Optional[int] = None
    activity_type: Optional[ActivityType] = None
    task_status: Optional[TaskStatus] = None
    event_status: Optional[EventStatus] = None
    date: Optional[datetime.date] = None
    url: Optional[Annotated[AnyUrl, MaxLen(500)]] = None
    event_type: Optional[CalendarEventType] = None
    challenge_id: Optional[int] = None
    reviewed_at: Optional[datetime.datetime] = None
    review_note: Optional[Annotated[str, MaxLen(1000)]] = None
