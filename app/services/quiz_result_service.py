from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.quiz_result import QuizResult
from app.repositories.quiz_result_repository import QuizResultRepository
from app.repositories.user_points_repository import UserPointsRepository
from app.schemas.quiz_result import QuizResultCreateDTO, QuizResultReadDTO, QuizResultUpdateDTO
from app.schemas.user_points import UserPointsCreateDTO, UserPointsUpdateDTO
from app.core.points_utils import recalculate_level


class QuizResultService:
    def __init__(self, repo: QuizResultRepository, points_repo: UserPointsRepository):
        self.repo = repo
        self.points_repo = points_repo

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

            if obj.points_earned:
                await self._adjust_points(obj.user_id, obj.points_earned)

            await self.repo.session.commit()
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Referenced user or quiz not found")
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QuizResult creation error")
        return QuizResultReadDTO.model_validate(obj)

    async def update(self, result_id: int, data: QuizResultUpdateDTO) -> QuizResultReadDTO:
        obj = await self._get_or_404(result_id)
        old_points = obj.points_earned or 0
        try:
            obj = await self.repo.update(obj, data)

            if data.points_earned is not None:
                delta = (data.points_earned or 0) - old_points
                if delta != 0:
                    await self._adjust_points(obj.user_id, delta)

            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QuizResult update error")
        return QuizResultReadDTO.model_validate(obj)

    async def delete(self, result_id: int) -> None:
        obj = await self._get_or_404(result_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QuizResult delete error")

    async def _adjust_points(self, user_id: int, delta: int) -> None:
        pts = await self.points_repo.get_by_user_id(user_id)
        if pts:
            new_total = max(0, pts.total_points + delta)
            level, level_name, points_to_next = recalculate_level(new_total)
            await self.points_repo.update(pts, UserPointsUpdateDTO(
                total_points=new_total,
                level=level,
                level_name=level_name,
                points_to_next_level=points_to_next,
            ))
        elif delta > 0:
            level, level_name, points_to_next = recalculate_level(delta)
            await self.points_repo.create(UserPointsCreateDTO(
                user_id=user_id,
                total_points=delta,
                level=level,
                level_name=level_name,
                points_to_next_level=points_to_next,
            ))
