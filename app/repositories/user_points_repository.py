from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_points import UserPoints
from app.schemas.user_points import UserPointsCreateDTO, UserPointsUpdateDTO


class UserPointsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: int) -> Optional[UserPoints]:
        return await self.session.get(UserPoints, user_id)

    async def create(self, data: UserPointsCreateDTO) -> UserPoints:
        points = UserPoints(**data.model_dump())
        self.session.add(points)
        await self.session.flush()
        await self.session.refresh(points)
        return points

    async def delete(self, points: UserPoints) -> None:
        await self.session.delete(points)
        await self.session.flush()

    async def update(self, points: UserPoints, data: UserPointsUpdateDTO) -> UserPoints:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(points, field, value)
        await self.session.flush()
        await self.session.refresh(points)
        return points

    async def get_leaderboard(self) -> list[tuple[UserPoints, int]]:
        """Возвращает записи, отсортированные по убыванию баллов, с рангом."""
        stmt = select(UserPoints).order_by(UserPoints.total_points.desc())
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [(record, rank + 1) for rank, record in enumerate(records)]
