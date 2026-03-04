from typing import Optional

from app.schemas.base import BaseDTO


class MentorJuniorCreateDTO(BaseDTO):
    mentor_id: int
    junior_id: int
    assigned_by: int


class MentorJuniorReadDTO(BaseDTO):
    mentor_id: int
    junior_id: int
    assigned_by: int


class MentorJuniorUpdateDTO(BaseDTO):
    mentor_id: Optional[int] = None
    junior_id: Optional[int] = None
    assigned_by: Optional[int] = None
