from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.challenge_employee import ChallengeEmployee
from app.repositories.challenge_employee_repository import ChallengeEmployeeRepository
from app.repositories.user_points_repository import UserPointsRepository
from app.schemas.challenge_employee import ChallengeEmployeeCreateDTO, ChallengeEmployeeReadDTO, ChallengeEmployeeUpdateDTO
from app.schemas.user_points import UserPointsCreateDTO, UserPointsUpdateDTO
from app.core.points_utils import recalculate_level


class ChallengeEmployeeService:
    def __init__(
        self,
        challenge_employee_repo: ChallengeEmployeeRepository,
        points_repo: UserPointsRepository,
    ):
        self.challenge_employee_repo = challenge_employee_repo
        self.points_repo = points_repo

    async def _get_or_404(self, challenge_id: int, employee_id: int) -> ChallengeEmployee:
        obj = await self.challenge_employee_repo.get_by_id(challenge_id, employee_id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ChallengeEmployee with challenge_id={challenge_id} and employee_id={employee_id} not found",
            )
        return obj

    async def get_by_id(self, challenge_id: int, employee_id: int) -> ChallengeEmployeeReadDTO:
        obj = await self._get_or_404(challenge_id, employee_id)
        return ChallengeEmployeeReadDTO.model_validate(obj)

    async def create(self, data: ChallengeEmployeeCreateDTO) -> ChallengeEmployeeReadDTO:
        existing = await self.challenge_employee_repo.get_by_id(data.challenge_id, data.employee_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="ChallengeEmployee pair already exists",
            )
        try:
            obj = await self.challenge_employee_repo.create(data)
            await self.challenge_employee_repo.session.commit()
        except IntegrityError:
            await self.challenge_employee_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="ChallengeEmployee pair already exists or referenced entity not found",
            )
        except SQLAlchemyError:
            await self.challenge_employee_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ChallengeEmployee creation error",
            )
        return ChallengeEmployeeReadDTO.model_validate(obj)

    async def delete(self, challenge_id: int, employee_id: int) -> None:
        obj = await self._get_or_404(challenge_id, employee_id)
        if obj.awarded_points:
            await self._adjust_points(obj.employee_id, -obj.awarded_points)
        try:
            await self.challenge_employee_repo.delete(obj)
            await self.challenge_employee_repo.session.commit()
        except SQLAlchemyError:
            await self.challenge_employee_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ChallengeEmployee delete error",
            )

    async def update(
        self, challenge_id: int, employee_id: int, data: ChallengeEmployeeUpdateDTO
    ) -> ChallengeEmployeeReadDTO:
        obj = await self._get_or_404(challenge_id, employee_id)
        old_awarded = obj.awarded_points or 0
        try:
            obj = await self.challenge_employee_repo.update(obj, data)
            if data.awarded_points is not None:
                delta = (data.awarded_points or 0) - old_awarded
                if delta != 0:
                    await self._adjust_points(employee_id, delta)
            await self.challenge_employee_repo.session.commit()
        except IntegrityError:
            await self.challenge_employee_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="ChallengeEmployee pair already exists or referenced entity not found",
            )
        except SQLAlchemyError:
            await self.challenge_employee_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ChallengeEmployee update error",
            )
        return ChallengeEmployeeReadDTO.model_validate(obj)

    async def get_all(self, employee_id: Optional[int] = None, assigned_by: Optional[int] = None) -> list[ChallengeEmployeeReadDTO]:
        assignments = await self.challenge_employee_repo.get_all(employee_id=employee_id, assigned_by=assigned_by)
        return [ChallengeEmployeeReadDTO.model_validate(a) for a in assignments]

    async def rollback_points_for_challenge(self, challenge_id: int) -> None:
        assignments = await self.challenge_employee_repo.get_all_by_challenge_id(challenge_id)
        for a in assignments:
            if a.awarded_points:
                await self._adjust_points(a.employee_id, -a.awarded_points)
                a.awarded_points = None
        await self.challenge_employee_repo.session.flush()

    async def skip_unfinished_for_challenge(self, challenge_id: int) -> None:
        from app.core.enums import ChallengeEmployeeProgress
        assignments = await self.challenge_employee_repo.get_all_by_challenge_id(challenge_id)
        for a in assignments:
            if a.progress in (ChallengeEmployeeProgress.GOING, ChallengeEmployeeProgress.IN_PROGRESS):
                a.progress = ChallengeEmployeeProgress.SKIPPED
        await self.challenge_employee_repo.session.flush()

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
