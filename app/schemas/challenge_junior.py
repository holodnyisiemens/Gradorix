from typing import Optional

from app.schemas.base import BaseDTO
from app.core.enums import ChallengeJuniorProgress


class ChallengeJuniorCreateDTO(BaseDTO):
    activity_id: int
    junior_id: int
    assigned_by: int
    progress: ChallengeJuniorProgress = ChallengeJuniorProgress.GOING


class ChallengeJuniorReadDTO(BaseDTO):
    activity_id: int
    junior_id: int
    assigned_by: int
    progress: ChallengeJuniorProgress


class ChallengeJuniorUpdateDTO(BaseDTO):
    activity_id: Optional[int] = None
    junior_id: Optional[int] = None
    assigned_by: Optional[int] = None
    progress: Optional[ChallengeJuniorProgress] = None
