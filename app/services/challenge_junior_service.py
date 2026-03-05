from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.challenge_junior import ChallengeJunior
from app.repositories.challenge_junior_repository import ChallengeJuniorRepository
from app.schemas.challenge_junior import ChallengeJuniorCreateDTO, ChallengeJuniorReadDTO, ChallengeJuniorUpdateDTO


class ChallengeJuniorService:
    def __init__(self, challenge_junior_repo: ChallengeJuniorRepository):
        self.challenge_junior_repo = challenge_junior_repo

    async def _get_or_404(self, challenge_id: int, junior_id: int) -> ChallengeJunior:
        """Проверка существования назначения"""
        challenge_junior = await self.challenge_junior_repo.get_by_id(challenge_id, junior_id)
        if not challenge_junior:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ChallengeJunior with challenge_id={challenge_id} and junior_id={junior_id} not found",
            )
        return challenge_junior

    async def get_by_id(self, challenge_id: int, junior_id: int) -> ChallengeJuniorReadDTO:
        """Получить назначение по ключу"""
        challenge_junior = await self._get_or_404(challenge_id, junior_id)
        return ChallengeJuniorReadDTO.model_validate(challenge_junior)

    async def create(self, data: ChallengeJuniorCreateDTO) -> ChallengeJuniorReadDTO:
        """Создать назначение челленджа джуниору"""
        existing = await self.challenge_junior_repo.get_by_id(data.challenge_id, data.junior_id)
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

    async def delete(self, challenge_id: int, junior_id: int) -> None:
        """Удалить назначение"""
        challenge_junior = await self._get_or_404(challenge_id, junior_id)

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
        self, challenge_id: int, junior_id: int, data: ChallengeJuniorUpdateDTO
    ) -> ChallengeJuniorReadDTO:
        """Обновить назначение"""
        challenge_junior = await self._get_or_404(challenge_id, junior_id)

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

    async def get_all(self) -> list[ChallengeJuniorReadDTO]:
        """Получить все назначения"""
        assignments = await self.challenge_junior_repo.get_all()
        return [ChallengeJuniorReadDTO.model_validate(a) for a in assignments]
