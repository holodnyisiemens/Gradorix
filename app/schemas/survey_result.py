import datetime
from typing import Optional

from app.schemas.base import BaseDTO


class SurveyResultCreateDTO(BaseDTO):
    quiz_id: int
    completed_at: datetime.date
    answers: Optional[list] = None


class SurveyResultReadDTO(BaseDTO):
    id: int
    user_id: int
    quiz_id: int
    score: int
    completed_at: datetime.date
    points_earned: int
    answers: Optional[list] = None


class SurveyResultUpdateDTO(BaseDTO):
    completed_at: Optional[datetime.date] = None
    answers: Optional[list] = None
