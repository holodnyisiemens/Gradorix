from typing import Annotated, Optional

from annotated_types import MaxLen

from app.schemas.base import BaseDTO


class UserPointsCreateDTO(BaseDTO):
    user_id: int
    total_points: int = 0
    level: int = 1
    level_name: Annotated[str, MaxLen(50)] = "Новичок"
    points_to_next_level: int = 100


class UserPointsReadDTO(BaseDTO):
    user_id: int
    total_points: int
    level: int
    level_name: str
    points_to_next_level: int
    rank: Optional[int] = None  # вычисляется динамически


class UserPointsUpdateDTO(BaseDTO):
    total_points: Optional[int] = None
    level: Optional[int] = None
    level_name: Optional[Annotated[str, MaxLen(50)]] = None
    points_to_next_level: Optional[int] = None
