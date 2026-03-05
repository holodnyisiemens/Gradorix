from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.challenge import Challenge
from app.repositories.challenge_repository import ChallengeRepository
from app.schemas.challenge import ChallengeCreateDTO, ChallengeReadDTO, ChallengeUpdateDTO


class ChallengeService:
    def __init__(self, challenge_repo: ChallengeRepository):
        self.challenge_repo = challenge_repo

    async def _get_or_404(self, challenge_id: int) -> Challenge:
        """Проверка существования челленджа"""
        challenge = await self.challenge_repo.get_by_id(challenge_id)
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Challenge with ID {challenge_id} not found",
            )
        return challenge

    async def get_by_id(self, challenge_id: int) -> ChallengeReadDTO:
        """Получить челлендж по ID"""
        challenge = await self._get_or_404(challenge_id)
        return ChallengeReadDTO.model_validate(challenge)

    async def create(self, data: ChallengeCreateDTO) -> ChallengeReadDTO:
        """Создать челлендж"""
        try:
            challenge = await self.challenge_repo.create(data)
            await self.challenge_repo.session.commit()
        except SQLAlchemyError:
            await self.challenge_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Challenge creation error",
            )

        return ChallengeReadDTO.model_validate(challenge)

    async def delete(self, challenge_id: int) -> None:
        """Удалить челлендж"""
        challenge = await self._get_or_404(challenge_id)

        try:
            await self.challenge_repo.delete(challenge)
            await self.challenge_repo.session.commit()
        except SQLAlchemyError:
            await self.challenge_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Challenge delete error",
            )

    async def update(
        self, challenge_id: int, data: ChallengeUpdateDTO
    ) -> ChallengeReadDTO:
        """Обновить челлендж"""
        challenge = await self._get_or_404(challenge_id)

        try:
            challenge = await self.challenge_repo.update(challenge, data)
            await self.challenge_repo.session.commit()
        except SQLAlchemyError:
            await self.challenge_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Challenge update error",
            )

        return ChallengeReadDTO.model_validate(challenge)

    async def get_all(self) -> list[ChallengeReadDTO]:
        """Получить все челленджи"""
        challenges = await self.challenge_repo.get_all()
        return [ChallengeReadDTO.model_validate(c) for c in challenges]
