from typing import Optional

from app.schemas.base import BaseDTO
from app.schemas.enums import ChallengeJuniorProgress


class ChallengeJuniorCreateDTO(BaseDTO):
    challenge_id: int
    junior_id: int
    assigned_by: int
    progress: ChallengeJuniorProgress


class ChallengeJuniorReadDTO(BaseDTO):
    challenge_id: int
    junior_id: int
    assigned_by: int
    progress: ChallengeJuniorProgress


class ChallengeJuniorUpdateDTO(BaseDTO):
    challenge_id: Optional[int] = None
    junior_id: Optional[int] = None
    assigned_by: Optional[int] = None
    progress: Optional[ChallengeJuniorProgress] = None
