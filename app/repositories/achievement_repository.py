from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement
from app.schemas.achievement import AchievementCreateDTO, AchievementUpdateDTO


class AchievementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, achievement_id: int) -> Optional[Achievement]:
        return await self.session.get(Achievement, achievement_id)

    async def create(self, data: AchievementCreateDTO) -> Achievement:
        achievement = Achievement(**data.model_dump())
        self.session.add(achievement)
        await self.session.flush()
        await self.session.refresh(achievement)
        return achievement

    async def delete(self, achievement: Achievement) -> None:
        await self.session.delete(achievement)
        await self.session.flush()

    async def update(self, achievement: Achievement, data: AchievementUpdateDTO) -> Achievement:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(achievement, field, value)
        await self.session.flush()
        await self.session.refresh(achievement)
        return achievement

    async def get_all(self) -> list[Achievement]:
        stmt = select(Achievement)
        result = await self.session.execute(stmt)
        return result.scalars().all()
