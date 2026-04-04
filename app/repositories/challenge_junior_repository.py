from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge_junior import ChallengeJunior
from app.schemas.challenge_junior import ChallengeJuniorCreateDTO, ChallengeJuniorUpdateDTO


class ChallengeJuniorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, activity_id: int, junior_id: int) -> Optional[ChallengeJunior]:
        return await self.session.get(ChallengeJunior, (activity_id, junior_id))

    async def create(self, challenge_junior_data: ChallengeJuniorCreateDTO) -> ChallengeJunior:
        challenge_junior = ChallengeJunior(**challenge_junior_data.model_dump())
        self.session.add(challenge_junior)

        await self.session.flush()
        await self.session.refresh(challenge_junior)

        return challenge_junior

    async def delete(self, challenge_junior: ChallengeJunior) -> None:
        await self.session.delete(challenge_junior)
        await self.session.flush()

    async def update(self, challenge_junior: ChallengeJunior, challenge_junior_data: ChallengeJuniorUpdateDTO) -> ChallengeJunior:
        update_data = challenge_junior_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(challenge_junior, field, value)

        await self.session.flush()
        await self.session.refresh(challenge_junior)

        return challenge_junior

    async def get_all(self, junior_id: Optional[int] = None, assigned_by: Optional[int] = None) -> list[ChallengeJunior]:
        stmt = select(ChallengeJunior)
        if junior_id is not None:
            stmt = stmt.where(ChallengeJunior.junior_id == junior_id)
        if assigned_by is not None:
            stmt = stmt.where(ChallengeJunior.assigned_by == assigned_by)
        result = await self.session.execute(stmt)
        return result.scalars().all()
