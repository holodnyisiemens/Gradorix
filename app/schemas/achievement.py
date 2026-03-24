from typing import Annotated, Optional

from annotated_types import MaxLen

from app.core.enums import AchievementCategory
from app.schemas.base import BaseDTO


class AchievementCreateDTO(BaseDTO):
    title: Annotated[str, MaxLen(255)]
    description: Annotated[str, MaxLen(1000)]
    icon: Annotated[str, MaxLen(10)]
    category: AchievementCategory
    xp: int = 0


class AchievementReadDTO(BaseDTO):
    id: int
    title: str
    description: str
    icon: str
    category: AchievementCategory
    xp: int


class AchievementUpdateDTO(BaseDTO):
    title: Optional[Annotated[str, MaxLen(255)]] = None
    description: Optional[Annotated[str, MaxLen(1000)]] = None
    icon: Optional[Annotated[str, MaxLen(10)]] = None
    category: Optional[AchievementCategory] = None
    xp: Optional[int] = None
