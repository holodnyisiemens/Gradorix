import datetime
from typing import Optional

from app.schemas.base import BaseDTO


class MeetingAttendanceCreateDTO(BaseDTO):
    event_id: int
    user_id: int
    attended: bool = False
    marked_at: Optional[datetime.datetime] = None
    marked_by: Optional[int] = None


class MeetingAttendanceReadDTO(BaseDTO):
    id: int
    event_id: int
    user_id: int
    attended: bool
    marked_at: Optional[datetime.datetime] = None
    marked_by: Optional[int] = None


class MeetingAttendanceUpdateDTO(BaseDTO):
    attended: Optional[bool] = None
    marked_at: Optional[datetime.datetime] = None
    marked_by: Optional[int] = None
