from typing import Any, Optional, Annotated

from annotated_types import MaxLen

from app.schemas.base import BaseDTO


class SurveyCreateDTO(BaseDTO):
    title: Annotated[str, MaxLen(255)]
    description: Annotated[str, MaxLen(1000)]
    category: Annotated[str, MaxLen(100)]
    duration_min: int = 10
    questions: list[Any] = []
    available: bool = True


class SurveyReadDTO(BaseDTO):
    id: int
    title: str
    description: str
    category: str
    duration_min: int
    questions: list[Any]
    available: bool


class SurveyUpdateDTO(BaseDTO):
    title: Optional[Annotated[str, MaxLen(255)]] = None
    description: Optional[Annotated[str, MaxLen(1000)]] = None
    category: Optional[Annotated[str, MaxLen(100)]] = None
    duration_min: Optional[int] = None
    questions: Optional[list[Any]] = None
    available: Optional[bool] = None
