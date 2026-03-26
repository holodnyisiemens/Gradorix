from typing import Annotated, Optional

from annotated_types import MaxLen

from app.core.enums import TeamStatus
from app.schemas.base import BaseDTO


class TeamCreateDTO(BaseDTO):
    name: Annotated[str, MaxLen(255)]
    project: Annotated[str, MaxLen(255)]
    status: TeamStatus = TeamStatus.ACTIVE
    mentor_id: Optional[int] = None
    description: Annotated[str, MaxLen(1000)] = ""
    member_ids: list[int] = []


class TeamReadDTO(BaseDTO):
    id: int
    name: str
    project: str
    status: TeamStatus
    mentor_id: Optional[int] = None
    description: str
    member_ids: list[int] = []


class TeamUpdateDTO(BaseDTO):
    name: Optional[Annotated[str, MaxLen(255)]] = None
    project: Optional[Annotated[str, MaxLen(255)]] = None
    status: Optional[TeamStatus] = None
    mentor_id: Optional[int] = None
    description: Optional[Annotated[str, MaxLen(1000)]] = None
    member_ids: Optional[list[int]] = None
