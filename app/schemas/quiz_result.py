import datetime
from typing import Optional

from app.schemas.base import BaseDTO


class QuizResultCreateDTO(BaseDTO):
    user_id: int
    quiz_id: int
    score: int  # 0-100
    completed_at: datetime.date
    points_earned: int = 0
    answers: Optional[list] = None  # text answers per question index


class QuizResultReadDTO(BaseDTO):
    id: int
    user_id: int
    quiz_id: int
    score: int
    completed_at: datetime.date
    points_earned: int
    answers: Optional[list] = None


class QuizResultUpdateDTO(BaseDTO):
    score: Optional[int] = None
    points_earned: Optional[int] = None
    answers: Optional[list] = None
