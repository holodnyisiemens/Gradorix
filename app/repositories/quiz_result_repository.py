from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz_result import QuizResult
from app.schemas.quiz_result import QuizResultCreateDTO, QuizResultUpdateDTO


class QuizResultRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, result_id: int) -> Optional[QuizResult]:
        return await self.session.get(QuizResult, result_id)

    async def create(self, data: QuizResultCreateDTO) -> QuizResult:
        qr = QuizResult(**data.model_dump())
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
    ) -> list[QuizResult]:
        stmt = select(QuizResult)
        if user_id is not None:
            stmt = stmt.where(QuizResult.user_id == user_id)
        if quiz_id is not None:
            stmt = stmt.where(QuizResult.quiz_id == quiz_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
