import datetime
from typing import Optional

from app.schemas.base import BaseDTO


class UserAchievementCreateDTO(BaseDTO):
    user_id: int
    achievement_id: int
    earned_at: Optional[datetime.date] = None


class UserAchievementReadDTO(BaseDTO):
    user_id: int
    achievement_id: int
    earned_at: Optional[datetime.date] = None


class UserAchievementUpdateDTO(BaseDTO):
    earned_at: Optional[datetime.date] = None
