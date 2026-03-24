from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.user_achievement import UserAchievement
from app.repositories.user_achievement_repository import UserAchievementRepository
from app.schemas.user_achievement import UserAchievementCreateDTO, UserAchievementReadDTO, UserAchievementUpdateDTO


class UserAchievementService:
    def __init__(self, repo: UserAchievementRepository):
        self.repo = repo

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
