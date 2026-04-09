import datetime
from typing import Annotated, Optional

from annotated_types import MaxLen

from app.core.enums import ActivityStatus, ActivityType
from app.schemas.base import BaseDTO


class ActivityCreateDTO(BaseDTO):
    user_id: int
    title: Annotated[str, MaxLen(255)]
    description: Annotated[str, MaxLen(1000)]
    activity_type: ActivityType = ActivityType.ACHIEVEMENT
    # HiPo doesn't set points — HR awards them during review
    requested_points: int = 0
    status: ActivityStatus = ActivityStatus.PENDING
    links: Optional[list[str]] = None
    achieved_date: Optional[datetime.date] = None


class ActivityReadDTO(BaseDTO):
    id: int
    user_id: int
    title: str
    description: str
    requested_points: int
    awarded_points: Optional[int] = None
    status: ActivityStatus
    activity_type: ActivityType
    submitted_at: datetime.datetime
    reviewed_at: Optional[datetime.datetime] = None
    review_note: Optional[str] = None
    links: Optional[list[str]] = None
    achieved_date: Optional[datetime.date] = None


class ActivityUpdateDTO(BaseDTO):
    title: Optional[Annotated[str, MaxLen(255)]] = None
    description: Optional[Annotated[str, MaxLen(1000)]] = None
    requested_points: Optional[int] = None
    awarded_points: Optional[int] = None
    status: Optional[ActivityStatus] = None
    activity_type: Optional[ActivityType] = None
    reviewed_at: Optional[datetime.datetime] = None
    review_note: Optional[Annotated[str, MaxLen(1000)]] = None
    links: Optional[list[str]] = None
    achieved_date: Optional[datetime.date] = None
