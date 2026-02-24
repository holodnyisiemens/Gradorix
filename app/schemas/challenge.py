from annotated_types import MaxLen
from typing import Annotated, Optional

from pydantic import AnyUrl

from app.schemas.base import BaseDTO


class ChallengeCreateDTO(BaseDTO):
    title: Annotated[str, MaxLen(255)]

    description: Optional[Annotated[str, MaxLen(1000)]]
    url: Optional[Annotated[AnyUrl, MaxLen(500)]]
    is_active: Optional[bool]


class ChallengeReadDTO(BaseDTO):
    id: int
    title: str
    description: str
    url: AnyUrl
    is_active: bool


class ChallengeUpdateDTO(BaseDTO):
    title: Optional[Annotated[str, MaxLen(255)]] = None
    description: Optional[Annotated[str, MaxLen(1000)]] = None
    url: Optional[Annotated[AnyUrl, MaxLen(500)]] = None
    is_active: Optional[bool] = None
