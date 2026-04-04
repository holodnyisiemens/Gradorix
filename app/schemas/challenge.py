import datetime
from annotated_types import MaxLen
from typing import Annotated, Optional

from pydantic import AnyUrl

from app.schemas.base import BaseDTO
from app.core.enums import TaskStatus


class ChallengeCreateDTO(BaseDTO):
    title: Annotated[str, MaxLen(255)]
    description: Optional[Annotated[str, MaxLen(1000)]] = None
    url: Optional[Annotated[AnyUrl, MaxLen(500)]] = None
    status: TaskStatus
    date: Optional[datetime.date] = None


class ChallengeReadDTO(BaseDTO):
    id: int
    title: str
    description: Optional[str]
    url: Optional[AnyUrl]
    status: TaskStatus
    date: Optional[datetime.date] = None


class ChallengeUpdateDTO(BaseDTO):
    title: Optional[Annotated[str, MaxLen(255)]] = None
    description: Optional[Annotated[str, MaxLen(1000)]] = None
    url: Optional[Annotated[AnyUrl, MaxLen(500)]] = None
    status: Optional[TaskStatus] = None
    date: Optional[datetime.date] = None
