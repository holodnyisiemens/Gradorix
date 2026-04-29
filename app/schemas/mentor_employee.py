from typing import Optional

from app.schemas.base import BaseDTO


class MentorEmployeeCreateDTO(BaseDTO):
    mentor_id: int
    employee_id: int
    assigned_by: int


class MentorEmployeeReadDTO(BaseDTO):
    mentor_id: int
    employee_id: int
    assigned_by: int


class MentorEmployeeUpdateDTO(BaseDTO):
    mentor_id: Optional[int] = None
    employee_id: Optional[int] = None
    assigned_by: Optional[int] = None
