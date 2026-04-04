from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.activity import Activity
from app.models.challenge_junior import ChallengeJunior
from app.repositories.activity_repository import ActivityRepository
from app.repositories.challenge_junior_repository import ChallengeJuniorRepository
from app.schemas.challenge_junior import ChallengeJuniorCreateDTO, ChallengeJuniorReadDTO, ChallengeJuniorUpdateDTO
from app.core.enums import ActivityType


class ChallengeJuniorService:
    def __init__(self, challenge_junior_repo: ChallengeJuniorRepository, activity_repo: ActivityRepository):
        self.challenge_junior_repo = challenge_junior_repo
        self.activity_repo = activity_repo

    async def _validate_activity_is_task(self, activity_id: int) -> Activity:
        """Verify that activity exists and is of type TASK"""
        activity = await self.activity_repo.get_by_id(activity_id)
        if not activity or activity.activity_type != ActivityType.TASK:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task activity with ID {activity_id} not found",
            )
        return activity

    async def _get_or_404(self, activity_id: int, junior_id: int) -> ChallengeJunior:
        """Проверка существования назначения"""
        challenge_junior = await self.challenge_junior_repo.get_by_id(activity_id, junior_id)
        if not challenge_junior:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ChallengeJunior with activity_id={activity_id} and junior_id={junior_id} not found",
            )
        return challenge_junior

    async def get_by_id(self, activity_id: int, junior_id: int) -> ChallengeJuniorReadDTO:
        """Получить назначение по ключу"""
        await self._validate_activity_is_task(activity_id)
        challenge_junior = await self._get_or_404(activity_id, junior_id)
        return ChallengeJuniorReadDTO.model_validate(challenge_junior)

    async def create(self, data: ChallengeJuniorCreateDTO) -> ChallengeJuniorReadDTO:
        """Создать назначение челленджа джуниору"""
        await self._validate_activity_is_task(data.activity_id)
        
        existing = await self.challenge_junior_repo.get_by_id(data.activity_id, data.junior_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="ChallengeJunior pair already exists",
            )

        try:
            challenge_junior = await self.challenge_junior_repo.create(data)
            await self.challenge_junior_repo.session.commit()
        except IntegrityError:
            await self.challenge_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="ChallengeJunior pair already exists or referenced entity not found",
            )
        except SQLAlchemyError:
            await self.challenge_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ChallengeJunior creation error",
            )

        return ChallengeJuniorReadDTO.model_validate(challenge_junior)

    async def delete(self, activity_id: int, junior_id: int) -> None:
        """Удалить назначение"""
        challenge_junior = await self._get_or_404(activity_id, junior_id)

        try:
            await self.challenge_junior_repo.delete(challenge_junior)
            await self.challenge_junior_repo.session.commit()
        except SQLAlchemyError:
            await self.challenge_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ChallengeJunior delete error",
            )

    async def update(
        self, activity_id: int, junior_id: int, data: ChallengeJuniorUpdateDTO
    ) -> ChallengeJuniorReadDTO:
        """Обновить назначение"""
        challenge_junior = await self._get_or_404(activity_id, junior_id)

        try:
            challenge_junior = await self.challenge_junior_repo.update(challenge_junior, data)
            await self.challenge_junior_repo.session.commit()
        except IntegrityError:
            await self.challenge_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="ChallengeJunior pair already exists or referenced entity not found",
            )
        except SQLAlchemyError:
            await self.challenge_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ChallengeJunior update error",
            )

        return ChallengeJuniorReadDTO.model_validate(challenge_junior)

    async def get_all(self, junior_id: Optional[int] = None, assigned_by: Optional[int] = None) -> list[ChallengeJuniorReadDTO]:
        """Получить все назначения, опционально с фильтрацией"""
        assignments = await self.challenge_junior_repo.get_all(junior_id=junior_id, assigned_by=assigned_by)
        return [ChallengeJuniorReadDTO.model_validate(a) for a in assignments]
