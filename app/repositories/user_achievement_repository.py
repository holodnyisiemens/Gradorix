from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_achievement import UserAchievement
from app.schemas.user_achievement import UserAchievementCreateDTO, UserAchievementUpdateDTO


class UserAchievementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int, achievement_id: int) -> Optional[UserAchievement]:
        return await self.session.get(UserAchievement, (user_id, achievement_id))

    async def create(self, data: UserAchievementCreateDTO) -> UserAchievement:
        ua = UserAchievement(**data.model_dump())
        self.session.add(ua)
        await self.session.flush()
        await self.session.refresh(ua)
        return ua

    async def delete(self, ua: UserAchievement) -> None:
        await self.session.delete(ua)
        await self.session.flush()

    async def update(self, ua: UserAchievement, data: UserAchievementUpdateDTO) -> UserAchievement:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(ua, field, value)
        await self.session.flush()
        await self.session.refresh(ua)
        return ua

    async def get_all(self, user_id: Optional[int] = None) -> list[UserAchievement]:
        stmt = select(UserAchievement)
        if user_id is not None:
            stmt = stmt.where(UserAchievement.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
