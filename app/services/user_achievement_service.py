from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.user_achievement import UserAchievement
from app.repositories.user_achievement_repository import UserAchievementRepository
from app.repositories.achievement_repository import AchievementRepository
from app.repositories.user_points_repository import UserPointsRepository
from app.schemas.user_achievement import UserAchievementCreateDTO, UserAchievementReadDTO, UserAchievementUpdateDTO
from app.schemas.user_points import UserPointsCreateDTO, UserPointsUpdateDTO
from app.core.points_utils import recalculate_level


class UserAchievementService:
    def __init__(
        self,
        repo: UserAchievementRepository,
        achievement_repo: AchievementRepository,
        points_repo: UserPointsRepository,
    ):
        self.repo = repo
        self.achievement_repo = achievement_repo
        self.points_repo = points_repo

    async def _get_or_404(self, user_id: int, achievement_id: int) -> UserAchievement:
        obj = await self.repo.get_by_id(user_id, achievement_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"UserAchievement user={user_id} achievement={achievement_id} not found")
        return obj

    async def get_by_id(self, user_id: int, achievement_id: int) -> UserAchievementReadDTO:
        return UserAchievementReadDTO.model_validate(await self._get_or_404(user_id, achievement_id))

    async def get_all(self, user_id: Optional[int] = None) -> list[UserAchievementReadDTO]:
        items = await self.repo.get_all(user_id=user_id)
        return [UserAchievementReadDTO.model_validate(i) for i in items]

    async def create(self, data: UserAchievementCreateDTO) -> UserAchievementReadDTO:
        try:
            obj = await self.repo.create(data)

            # Add achievement XP to user_points
            achievement = await self.achievement_repo.get_by_id(data.achievement_id)
            if achievement and achievement.xp:
                pts = await self.points_repo.get_by_user_id(data.user_id)
                if pts:
                    new_total = pts.total_points + achievement.xp
                    level, level_name, points_to_next = recalculate_level(new_total)
                    await self.points_repo.update(pts, UserPointsUpdateDTO(
                        total_points=new_total,
                        level=level,
                        level_name=level_name,
                        points_to_next_level=points_to_next,
                    ))
                else:
                    level, level_name, points_to_next = recalculate_level(achievement.xp)
                    await self.points_repo.create(UserPointsCreateDTO(
                        user_id=data.user_id,
                        total_points=achievement.xp,
                        level=level,
                        level_name=level_name,
                        points_to_next_level=points_to_next,
                    ))

            await self.repo.session.commit()
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="UserAchievement already exists or referenced entity not found")
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="UserAchievement creation error")
        return UserAchievementReadDTO.model_validate(obj)

    async def update(self, user_id: int, achievement_id: int, data: UserAchievementUpdateDTO) -> UserAchievementReadDTO:
        obj = await self._get_or_404(user_id, achievement_id)
        try:
            obj = await self.repo.update(obj, data)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="UserAchievement update error")
        return UserAchievementReadDTO.model_validate(obj)

    async def delete(self, user_id: int, achievement_id: int) -> None:
        obj = await self._get_or_404(user_id, achievement_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="UserAchievement delete error")
