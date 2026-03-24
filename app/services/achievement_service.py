from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from app.models.achievement import Achievement
from app.repositories.achievement_repository import AchievementRepository
from app.schemas.achievement import AchievementCreateDTO, AchievementReadDTO, AchievementUpdateDTO


class AchievementService:
    def __init__(self, repo: AchievementRepository):
        self.repo = repo

    async def _get_or_404(self, achievement_id: int) -> Achievement:
        obj = await self.repo.get_by_id(achievement_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Achievement {achievement_id} not found")
        return obj

    async def get_by_id(self, achievement_id: int) -> AchievementReadDTO:
        return AchievementReadDTO.model_validate(await self._get_or_404(achievement_id))

    async def get_all(self) -> list[AchievementReadDTO]:
        items = await self.repo.get_all()
        return [AchievementReadDTO.model_validate(a) for a in items]

    async def create(self, data: AchievementCreateDTO) -> AchievementReadDTO:
        try:
            obj = await self.repo.create(data)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Achievement creation error")
        return AchievementReadDTO.model_validate(obj)

    async def update(self, achievement_id: int, data: AchievementUpdateDTO) -> AchievementReadDTO:
        obj = await self._get_or_404(achievement_id)
        try:
            obj = await self.repo.update(obj, data)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Achievement update error")
        return AchievementReadDTO.model_validate(obj)

    async def delete(self, achievement_id: int) -> None:
        obj = await self._get_or_404(achievement_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Achievement delete error")
