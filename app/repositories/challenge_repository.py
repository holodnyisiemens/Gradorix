from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge import Challenge
from app.schemas.challenge import ChallengeCreateDTO, ChallengeUpdateDTO


class ChallengeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, challenge_id: int) -> Optional[Challenge]:
        return await self.session.get(Challenge, challenge_id)

    async def create(self, challenge_data: ChallengeCreateDTO) -> Challenge:
        challenge = Challenge(**challenge_data.model_dump())
        self.session.add(challenge)

        await self.session.flush()
        await self.session.refresh(challenge)

        return challenge

    async def delete(self, challenge: Challenge) -> None:
        await self.session.delete(challenge)
        await self.session.flush()

    async def update(self, challenge: Challenge, challenge_data: ChallengeUpdateDTO) -> Challenge:
        update_data = challenge_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(challenge, field, value)

        await self.session.flush()
        await self.session.refresh(challenge)

        return challenge

    async def get_all(self) -> list[Challenge]:
        stmt = select(Challenge)
        result = await self.session.execute(stmt)
        return result.scalars().all()
