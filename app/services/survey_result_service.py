from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status

from app.models.quiz import Quiz
from app.models.quiz_result import QuizResult
from app.repositories.quiz_repository import QuizRepository
from app.repositories.quiz_result_repository import QuizResultRepository
from app.schemas.survey_result import SurveyResultCreateDTO, SurveyResultReadDTO, SurveyResultUpdateDTO


class SurveyResultService:
    def __init__(self, repo: QuizResultRepository, quiz_repo: QuizRepository):
        self.repo = repo
        self.quiz_repo = quiz_repo

    async def _get_or_404(self, result_id: int) -> QuizResult:
        obj = await self.repo.get_by_id(result_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"SurveyResult {result_id} not found")
        quiz = await self.quiz_repo.get_by_id(obj.quiz_id)
        if not quiz or not quiz.is_survey:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"SurveyResult {result_id} not found")
        return obj

    async def _get_survey_or_404(self, survey_id: int) -> Quiz:
        quiz = await self.quiz_repo.get_by_id(survey_id)
        if not quiz or not quiz.is_survey:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Survey {survey_id} not found")
        return quiz

    async def get_by_id(self, result_id: int) -> SurveyResultReadDTO:
        return SurveyResultReadDTO.model_validate(await self._get_or_404(result_id))

    async def get_all(
        self,
        user_id: Optional[int] = None,
        survey_id: Optional[int] = None,
    ) -> list[SurveyResultReadDTO]:
        items = await self.repo.get_all(user_id=user_id, quiz_id=survey_id, is_survey=True)
        return [SurveyResultReadDTO.model_validate(r) for r in items]

    async def create(self, user_id: int, data: SurveyResultCreateDTO) -> SurveyResultReadDTO:
        await self._get_survey_or_404(data.quiz_id)
        if await self.repo.exists_for_user(user_id, data.quiz_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Survey already completed by this user",
            )
        payload = data.model_dump()
        payload["user_id"] = user_id
        payload["score"] = 0
        payload["points_earned"] = 0

        try:
            obj = await self.repo.create(payload)
            await self.repo.session.commit()
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Referenced user or survey not found")
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SurveyResult creation error")
        return SurveyResultReadDTO.model_validate(obj)

    async def update(self, result_id: int, data: SurveyResultUpdateDTO) -> SurveyResultReadDTO:
        obj = await self._get_or_404(result_id)
        try:
            obj = await self.repo.update(obj, data)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SurveyResult update error")
        return SurveyResultReadDTO.model_validate(obj)

    async def delete(self, result_id: int) -> None:
        obj = await self._get_or_404(result_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SurveyResult delete error")

    async def get_statistics(self, survey_id: int) -> dict:
        await self._get_survey_or_404(survey_id)
        return await self.repo.get_statistics(survey_id)
