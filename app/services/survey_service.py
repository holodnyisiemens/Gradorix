from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from app.models.quiz import Quiz
from app.repositories.quiz_repository import QuizRepository
from app.repositories.quiz_result_repository import QuizResultRepository
from app.schemas.survey import SurveyCreateDTO, SurveyReadDTO, SurveyUpdateDTO


class SurveyService:
    def __init__(self, repo: QuizRepository, result_repo: QuizResultRepository | None = None):
        self.repo = repo
        self.result_repo = result_repo

    async def _get_or_404(self, survey_id: int) -> Quiz:
        obj = await self.repo.get_by_id(survey_id)
        if not obj or not obj.is_survey:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Survey {survey_id} not found")
        return obj

    async def _ensure_not_completed(self, user_id: int, survey_id: int) -> None:
        if self.result_repo and await self.result_repo.exists_for_user(user_id, survey_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Survey already completed",
            )

    async def get_by_id(
        self,
        survey_id: int,
        user_id: Optional[int] = None,
        block_if_completed: bool = False,
    ) -> SurveyReadDTO:
        obj = await self._get_or_404(survey_id)
        if block_if_completed and user_id is not None:
            await self._ensure_not_completed(user_id, survey_id)
        return SurveyReadDTO.model_validate(obj)

    async def get_all(
        self,
        available: Optional[bool] = None,
        exclude_completed_for_user_id: Optional[int] = None,
    ) -> list[SurveyReadDTO]:
        items = await self.repo.get_all(available=available, is_survey=True)
        if exclude_completed_for_user_id is not None and self.result_repo is not None:
            completed_ids = await self.result_repo.get_completed_quiz_ids(
                exclude_completed_for_user_id, is_survey=True,
            )
            items = [s for s in items if s.id not in completed_ids]
        return [SurveyReadDTO.model_validate(s) for s in items]

    async def create(self, data: SurveyCreateDTO) -> SurveyReadDTO:
        try:
            obj = await self.repo.create(data, is_survey=True)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Survey creation error")
        return SurveyReadDTO.model_validate(obj)

    async def update(self, survey_id: int, data: SurveyUpdateDTO) -> SurveyReadDTO:
        obj = await self._get_or_404(survey_id)
        try:
            obj = await self.repo.update(obj, data)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Survey update error")
        return SurveyReadDTO.model_validate(obj)

    async def delete(self, survey_id: int) -> None:
        obj = await self._get_or_404(survey_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Survey delete error")
