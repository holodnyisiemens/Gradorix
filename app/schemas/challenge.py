from annotated_types import MaxLen
from typing import Annotated, Optional

from pydantic import AnyUrl

from app.schemas.base import BaseDTO
from app.schemas.enums import ChallengeStatus


class ChallengeCreateDTO(BaseDTO):
    title: Annotated[str, MaxLen(255)]
    description: Optional[Annotated[str, MaxLen(1000)]] = None
    url: Optional[Annotated[AnyUrl, MaxLen(500)]] = None
    status: ChallengeStatus


class ChallengeReadDTO(BaseDTO):
    id: int
    title: str
    description: Optional[str]
    url: Optional[AnyUrl]
    status: ChallengeStatus


class ChallengeUpdateDTO(BaseDTO):
    title: Optional[Annotated[str, MaxLen(255)]] = None
    description: Optional[Annotated[str, MaxLen(1000)]] = None
    url: Optional[Annotated[AnyUrl, MaxLen(500)]] = None
    status: Optional[ChallengeStatus] = None
