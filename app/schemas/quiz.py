from typing import Any, Annotated, Optional

from annotated_types import MaxLen

from app.schemas.base import BaseDTO


class QuizCreateDTO(BaseDTO):
    title: Annotated[str, MaxLen(255)]
    description: Annotated[str, MaxLen(1000)]
    category: Annotated[str, MaxLen(100)]
    duration_min: int = 10
    questions: list[Any] = []  # [{id, text, type, options?, correctAnswers?}]
    points: int = 0
    available: bool = True


class QuizReadDTO(BaseDTO):
    id: int
    title: str
    description: str
    category: str
    duration_min: int
    questions: list[Any]
    points: int
    available: bool


class QuizUpdateDTO(BaseDTO):
    title: Optional[Annotated[str, MaxLen(255)]] = None
    description: Optional[Annotated[str, MaxLen(1000)]] = None
    category: Optional[Annotated[str, MaxLen(100)]] = None
    duration_min: Optional[int] = None
    questions: Optional[list[Any]] = None
    points: Optional[int] = None
    available: Optional[bool] = None
