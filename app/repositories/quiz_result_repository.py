from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz import Quiz
from app.models.quiz_result import QuizResult
from app.schemas.quiz_result import QuizResultCreateDTO, QuizResultUpdateDTO


class QuizResultRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, result_id: int) -> Optional[QuizResult]:
        return await self.session.get(QuizResult, result_id)

    async def create(self, data: QuizResultCreateDTO | dict) -> QuizResult:
        payload = data.model_dump() if hasattr(data, "model_dump") else data
        qr = QuizResult(**payload)
        self.session.add(qr)
        await self.session.flush()
        await self.session.refresh(qr)
        return qr

    async def update(self, qr: QuizResult, data: QuizResultUpdateDTO) -> QuizResult:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(qr, field, value)
        await self.session.flush()
        await self.session.refresh(qr)
        return qr

    async def delete(self, qr: QuizResult) -> None:
        await self.session.delete(qr)
        await self.session.flush()

    async def get_all(
        self,
        user_id: Optional[int] = None,
        quiz_id: Optional[int] = None,
        is_survey: Optional[bool] = None,
    ) -> list[QuizResult]:
        stmt = select(QuizResult)
        if is_survey is not None:
            stmt = stmt.join(Quiz, QuizResult.quiz_id == Quiz.id).where(Quiz.is_survey == is_survey)
        if user_id is not None:
            stmt = stmt.where(QuizResult.user_id == user_id)
        if quiz_id is not None:
            stmt = stmt.where(QuizResult.quiz_id == quiz_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def exists_for_user(self, user_id: int, quiz_id: int) -> bool:
        stmt = (
            select(QuizResult.id)
            .where(QuizResult.user_id == user_id, QuizResult.quiz_id == quiz_id)
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_completed_quiz_ids(self, user_id: int, is_survey: bool) -> set[int]:
        stmt = (
            select(QuizResult.quiz_id)
            .join(Quiz, QuizResult.quiz_id == Quiz.id)
            .where(QuizResult.user_id == user_id, Quiz.is_survey == is_survey)
        )
        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    async def get_statistics(self, survey_id: int) -> dict:
        stmt = select(func.count(QuizResult.id), func.count(func.distinct(QuizResult.user_id))).where(
            QuizResult.quiz_id == survey_id,
        )
        result = await self.session.execute(stmt)
        total, unique_users = result.one()
        return {
            "survey_id": survey_id,
            "responses_count": total,
            "participants_count": unique_users,
        }
