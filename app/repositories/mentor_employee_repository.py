from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mentor_employee import MentorEmployee
from app.schemas.mentor_employee import MentorEmployeeCreateDTO, MentorEmployeeUpdateDTO


class MentorEmployeeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, mentor_id: int, employee_id: int) -> Optional[MentorEmployee]:
        return await self.session.get(MentorEmployee, (mentor_id, employee_id))

    async def create(self, data: MentorEmployeeCreateDTO) -> MentorEmployee:
        obj = MentorEmployee(**data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: MentorEmployee) -> None:
        await self.session.delete(obj)
        await self.session.flush()

    async def update(self, obj: MentorEmployee, data: MentorEmployeeUpdateDTO) -> MentorEmployee:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def get_all(self, mentor_id: Optional[int] = None, employee_id: Optional[int] = None) -> list[MentorEmployee]:
        stmt = select(MentorEmployee)
        if mentor_id is not None:
            stmt = stmt.where(MentorEmployee.mentor_id == mentor_id)
        if employee_id is not None:
            stmt = stmt.where(MentorEmployee.employee_id == employee_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
