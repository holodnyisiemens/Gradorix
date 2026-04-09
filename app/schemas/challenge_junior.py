from typing import Optional

from app.schemas.base import BaseDTO
from app.core.enums import ChallengeJuniorProgress


class ChallengeJuniorCreateDTO(BaseDTO):
    challenge_id: int
    junior_id: int
    assigned_by: int
    progress: ChallengeJuniorProgress = ChallengeJuniorProgress.GOING


class ChallengeJuniorReadDTO(BaseDTO):
    challenge_id: int
    junior_id: int
    assigned_by: int
    progress: ChallengeJuniorProgress
    comment: Optional[str] = None
    links: Optional[list[str]] = None
    awarded_points: Optional[int] = None
    feedback: Optional[str] = None


class ChallengeJuniorUpdateDTO(BaseDTO):
    progress: Optional[ChallengeJuniorProgress] = None
    # Fields junior can fill in
    comment: Optional[str] = None
    links: Optional[list[str]] = None
    # Fields HR fills in
    awarded_points: Optional[int] = None
    feedback: Optional[str] = None
