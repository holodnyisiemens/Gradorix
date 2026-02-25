from typing import Optional

from app.schemas.base import BaseDTO


class MentorJuniorCreateDTO(BaseDTO):
    mentor_id: int
    junior_id: int


class MentorJuniorReadDTO(BaseDTO):
    mentor_id: int
    junior_id: int


class MentorJuniorUpdateDTO(BaseDTO):
    mentor_id: Optional[int] = None
    junior_id: Optional[int] = None
