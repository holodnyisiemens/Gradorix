from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz import Quiz
from app.schemas.base import BaseDTO
from app.schemas.quiz import QuizUpdateDTO


class QuizRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, quiz_id: int) -> Optional[Quiz]:
        return await self.session.get(Quiz, quiz_id)

    async def create(self, data: BaseDTO, is_survey: bool = False) -> Quiz:
        quiz = Quiz(**data.model_dump(), is_survey=is_survey)
        self.session.add(quiz)
        await self.session.flush()
        await self.session.refresh(quiz)
        return quiz

    async def delete(self, quiz: Quiz) -> None:
        await self.session.delete(quiz)
        await self.session.flush()

    async def update(self, quiz: Quiz, data: QuizUpdateDTO) -> Quiz:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(quiz, field, value)
        await self.session.flush()
        await self.session.refresh(quiz)
        return quiz

    async def get_all(self, available: Optional[bool] = None, is_survey: Optional[bool] = None) -> list[Quiz]:
        stmt = select(Quiz)
        if available is not None:
            stmt = stmt.where(Quiz.available == available)
        if is_survey is not None:
            stmt = stmt.where(Quiz.is_survey == is_survey)
        result = await self.session.execute(stmt)
        return result.scalars().all()
