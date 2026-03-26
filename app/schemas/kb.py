import datetime
from typing import Annotated, Optional

from annotated_types import MaxLen

from app.schemas.base import BaseDTO


class KBSectionCreateDTO(BaseDTO):
    title: Annotated[str, MaxLen(255)]
    order: int = 0


class KBSectionReadDTO(BaseDTO):
    id: int
    title: str
    order: int


class KBSectionUpdateDTO(BaseDTO):
    title: Optional[Annotated[str, MaxLen(255)]] = None
    order: Optional[int] = None


class KBArticleCreateDTO(BaseDTO):
    section_id: int
    title: Annotated[str, MaxLen(255)]
    content: str
    created_at: datetime.date
    author: Annotated[str, MaxLen(100)]


class KBArticleReadDTO(BaseDTO):
    id: int
    section_id: int
    title: str
    content: str
    created_at: datetime.date
    author: str


class KBArticleUpdateDTO(BaseDTO):
    section_id: Optional[int] = None
    title: Optional[Annotated[str, MaxLen(255)]] = None
    content: Optional[str] = None
    created_at: Optional[datetime.date] = None
    author: Optional[Annotated[str, MaxLen(100)]] = None
