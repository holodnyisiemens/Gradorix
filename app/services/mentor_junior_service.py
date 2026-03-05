from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.mentor_junior import MentorJunior
from app.repositories.mentor_junior_repository import MentorJuniorRepository
from app.schemas.mentor_junior import MentorJuniorCreateDTO, MentorJuniorReadDTO, MentorJuniorUpdateDTO


class MentorJuniorService:
    def __init__(self, mentor_junior_repo: MentorJuniorRepository):
        self.mentor_junior_repo = mentor_junior_repo

    async def _get_or_404(self, mentor_id: int, junior_id: int) -> MentorJunior:
        """Проверка существования связи ментор-джуниор"""
        mentor_junior = await self.mentor_junior_repo.get_by_id(mentor_id, junior_id)
        if not mentor_junior:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"MentorJunior with mentor_id={mentor_id} and junior_id={junior_id} not found",
            )
        return mentor_junior

    async def get_by_id(self, mentor_id: int, junior_id: int) -> MentorJuniorReadDTO:
        """Получить связь ментор-джуниор по ключу"""
        mentor_junior = await self._get_or_404(mentor_id, junior_id)
        return MentorJuniorReadDTO.model_validate(mentor_junior)

    async def create(self, data: MentorJuniorCreateDTO) -> MentorJuniorReadDTO:
        """Создать связь ментор-джуниор"""
        existing = await self.mentor_junior_repo.get_by_id(data.mentor_id, data.junior_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="MentorJunior pair already exists",
            )

        try:
            mentor_junior = await self.mentor_junior_repo.create(data)
            await self.mentor_junior_repo.session.commit()
        except IntegrityError:
            await self.mentor_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="MentorJunior pair already exists or referenced user not found",
            )
        except SQLAlchemyError:
            await self.mentor_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MentorJunior creation error",
            )

        return MentorJuniorReadDTO.model_validate(mentor_junior)

    async def delete(self, mentor_id: int, junior_id: int) -> None:
        """Удалить связь ментор-джуниор"""
        mentor_junior = await self._get_or_404(mentor_id, junior_id)

        try:
            await self.mentor_junior_repo.delete(mentor_junior)
            await self.mentor_junior_repo.session.commit()
        except SQLAlchemyError:
            await self.mentor_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MentorJunior delete error",
            )

    async def update(
        self, mentor_id: int, junior_id: int, data: MentorJuniorUpdateDTO
    ) -> MentorJuniorReadDTO:
        """Обновить связь ментор-джуниор"""
        mentor_junior = await self._get_or_404(mentor_id, junior_id)

        try:
            mentor_junior = await self.mentor_junior_repo.update(mentor_junior, data)
            await self.mentor_junior_repo.session.commit()
        except IntegrityError:
            await self.mentor_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="MentorJunior pair already exists or referenced user not found",
            )
        except SQLAlchemyError:
            await self.mentor_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MentorJunior update error",
            )

        return MentorJuniorReadDTO.model_validate(mentor_junior)

    async def get_all(self) -> list[MentorJuniorReadDTO]:
        """Получить все связи ментор-джуниор"""
        pairs = await self.mentor_junior_repo.get_all()
        return [MentorJuniorReadDTO.model_validate(p) for p in pairs]
