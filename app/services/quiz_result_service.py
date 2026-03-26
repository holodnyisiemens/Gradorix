from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.quiz_result import QuizResult
from app.repositories.quiz_result_repository import QuizResultRepository
from app.schemas.quiz_result import QuizResultCreateDTO, QuizResultReadDTO


class QuizResultService:
    def __init__(self, repo: QuizResultRepository):
        self.repo = repo

    async def _get_or_404(self, result_id: int) -> QuizResult:
        obj = await self.repo.get_by_id(result_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"QuizResult {result_id} not found")
        return obj

    async def get_by_id(self, result_id: int) -> QuizResultReadDTO:
        return QuizResultReadDTO.model_validate(await self._get_or_404(result_id))

    async def get_all(
        self,
        user_id: Optional[int] = None,
        quiz_id: Optional[int] = None,
    ) -> list[QuizResultReadDTO]:
        items = await self.repo.get_all(user_id=user_id, quiz_id=quiz_id)
        return [QuizResultReadDTO.model_validate(r) for r in items]

    async def create(self, data: QuizResultCreateDTO) -> QuizResultReadDTO:
        try:
            obj = await self.repo.create(data)
            await self.repo.session.commit()
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Referenced user or quiz not found")
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QuizResult creation error")
        return QuizResultReadDTO.model_validate(obj)

    async def delete(self, result_id: int) -> None:
        obj = await self._get_or_404(result_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QuizResult delete error")
