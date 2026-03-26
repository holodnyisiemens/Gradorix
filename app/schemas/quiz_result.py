import datetime

from app.schemas.base import BaseDTO


class QuizResultCreateDTO(BaseDTO):
    user_id: int
    quiz_id: int
    score: int  # 0-100
    completed_at: datetime.date
    points_earned: int = 0


class QuizResultReadDTO(BaseDTO):
    id: int
    user_id: int
    quiz_id: int
    score: int
    completed_at: datetime.date
    points_earned: int
