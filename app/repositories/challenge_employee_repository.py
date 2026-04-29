from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge_employee import ChallengeEmployee
from app.schemas.challenge_employee import ChallengeEmployeeCreateDTO, ChallengeEmployeeUpdateDTO


class ChallengeEmployeeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, challenge_id: int, employee_id: int) -> Optional[ChallengeEmployee]:
        return await self.session.get(ChallengeEmployee, (challenge_id, employee_id))

    async def create(self, data: ChallengeEmployeeCreateDTO) -> ChallengeEmployee:
        obj = ChallengeEmployee(**data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ChallengeEmployee) -> None:
        await self.session.delete(obj)
        await self.session.flush()

    async def update(self, obj: ChallengeEmployee, data: ChallengeEmployeeUpdateDTO) -> ChallengeEmployee:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def get_all(self, employee_id: Optional[int] = None, assigned_by: Optional[int] = None) -> list[ChallengeEmployee]:
        stmt = select(ChallengeEmployee)
        if employee_id is not None:
            stmt = stmt.where(ChallengeEmployee.employee_id == employee_id)
        if assigned_by is not None:
            stmt = stmt.where(ChallengeEmployee.assigned_by == assigned_by)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_by_challenge_id(self, challenge_id: int) -> list[ChallengeEmployee]:
        stmt = select(ChallengeEmployee).where(ChallengeEmployee.challenge_id == challenge_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
