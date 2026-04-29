from typing import Optional

from app.schemas.base import BaseDTO
from app.core.enums import ChallengeEmployeeProgress


class ChallengeEmployeeCreateDTO(BaseDTO):
    challenge_id: int
    employee_id: int
    assigned_by: int
    progress: ChallengeEmployeeProgress = ChallengeEmployeeProgress.GOING


class ChallengeEmployeeReadDTO(BaseDTO):
    challenge_id: int
    employee_id: int
    assigned_by: int
    progress: ChallengeEmployeeProgress
    comment: Optional[str] = None
    links: Optional[list[str]] = None
    awarded_points: Optional[int] = None
    feedback: Optional[str] = None


class ChallengeEmployeeUpdateDTO(BaseDTO):
    progress: Optional[ChallengeEmployeeProgress] = None
    comment: Optional[str] = None
    links: Optional[list[str]] = None
    awarded_points: Optional[int] = None
    feedback: Optional[str] = None
