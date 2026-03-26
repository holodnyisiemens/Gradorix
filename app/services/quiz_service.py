from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from app.models.quiz import Quiz
from app.repositories.quiz_repository import QuizRepository
from app.schemas.quiz import QuizCreateDTO, QuizReadDTO, QuizUpdateDTO


class QuizService:
    def __init__(self, repo: QuizRepository):
        self.repo = repo

    async def _get_or_404(self, quiz_id: int) -> Quiz:
        obj = await self.repo.get_by_id(quiz_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quiz {quiz_id} not found")
        return obj

    async def get_by_id(self, quiz_id: int) -> QuizReadDTO:
        return QuizReadDTO.model_validate(await self._get_or_404(quiz_id))

    async def get_all(self, available: Optional[bool] = None) -> list[QuizReadDTO]:
        items = await self.repo.get_all(available=available)
        return [QuizReadDTO.model_validate(q) for q in items]

    async def create(self, data: QuizCreateDTO) -> QuizReadDTO:
        try:
            obj = await self.repo.create(data)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz creation error")
        return QuizReadDTO.model_validate(obj)

    async def update(self, quiz_id: int, data: QuizUpdateDTO) -> QuizReadDTO:
        obj = await self._get_or_404(quiz_id)
        try:
            obj = await self.repo.update(obj, data)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz update error")
        return QuizReadDTO.model_validate(obj)

    async def delete(self, quiz_id: int) -> None:
        obj = await self._get_or_404(quiz_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz delete error")
