from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.challenge_junior import ChallengeJunior
from app.repositories.challenge_junior_repository import ChallengeJuniorRepository
from app.repositories.user_points_repository import UserPointsRepository
from app.schemas.challenge_junior import ChallengeJuniorCreateDTO, ChallengeJuniorReadDTO, ChallengeJuniorUpdateDTO
from app.schemas.user_points import UserPointsCreateDTO, UserPointsUpdateDTO
from app.core.points_utils import recalculate_level


class ChallengeJuniorService:
    def __init__(
        self,
        challenge_junior_repo: ChallengeJuniorRepository,
        points_repo: UserPointsRepository,
    ):
        self.challenge_junior_repo = challenge_junior_repo
        self.points_repo = points_repo

    async def _get_or_404(self, challenge_id: int, junior_id: int) -> ChallengeJunior:
        challenge_junior = await self.challenge_junior_repo.get_by_id(challenge_id, junior_id)
        if not challenge_junior:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ChallengeJunior with challenge_id={challenge_id} and junior_id={junior_id} not found",
            )
        return challenge_junior

    async def get_by_id(self, challenge_id: int, junior_id: int) -> ChallengeJuniorReadDTO:
        challenge_junior = await self._get_or_404(challenge_id, junior_id)
        return ChallengeJuniorReadDTO.model_validate(challenge_junior)

    async def create(self, data: ChallengeJuniorCreateDTO) -> ChallengeJuniorReadDTO:
        existing = await self.challenge_junior_repo.get_by_id(data.challenge_id, data.junior_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="ChallengeJunior pair already exists",
            )

        try:
            challenge_junior = await self.challenge_junior_repo.create(data)
            await self.challenge_junior_repo.session.commit()
        except IntegrityError:
            await self.challenge_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="ChallengeJunior pair already exists or referenced entity not found",
            )
        except SQLAlchemyError:
            await self.challenge_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ChallengeJunior creation error",
            )

        return ChallengeJuniorReadDTO.model_validate(challenge_junior)

    async def delete(self, challenge_id: int, junior_id: int) -> None:
        challenge_junior = await self._get_or_404(challenge_id, junior_id)

        # Rollback awarded points before deleting
        if challenge_junior.awarded_points:
            await self._adjust_points(challenge_junior.junior_id, -challenge_junior.awarded_points)

        try:
            await self.challenge_junior_repo.delete(challenge_junior)
            await self.challenge_junior_repo.session.commit()
        except SQLAlchemyError:
            await self.challenge_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ChallengeJunior delete error",
            )

    async def update(
        self, challenge_id: int, junior_id: int, data: ChallengeJuniorUpdateDTO
    ) -> ChallengeJuniorReadDTO:
        challenge_junior = await self._get_or_404(challenge_id, junior_id)
        old_awarded = challenge_junior.awarded_points or 0

        try:
            challenge_junior = await self.challenge_junior_repo.update(challenge_junior, data)

            # Adjust user points if awarded_points changed
            if data.awarded_points is not None:
                delta = (data.awarded_points or 0) - old_awarded
                if delta != 0:
                    await self._adjust_points(junior_id, delta)

            await self.challenge_junior_repo.session.commit()
        except IntegrityError:
            await self.challenge_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="ChallengeJunior pair already exists or referenced entity not found",
            )
        except SQLAlchemyError:
            await self.challenge_junior_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ChallengeJunior update error",
            )

        return ChallengeJuniorReadDTO.model_validate(challenge_junior)

    async def get_all(self, junior_id: Optional[int] = None, assigned_by: Optional[int] = None) -> list[ChallengeJuniorReadDTO]:
        assignments = await self.challenge_junior_repo.get_all(junior_id=junior_id, assigned_by=assigned_by)
        return [ChallengeJuniorReadDTO.model_validate(a) for a in assignments]

    async def rollback_points_for_challenge(self, challenge_id: int) -> None:
        """Deduct awarded_points from all juniors for a cancelled challenge."""
        assignments = await self.challenge_junior_repo.get_all_by_challenge_id(challenge_id)
        for assignment in assignments:
            if assignment.awarded_points:
                await self._adjust_points(assignment.junior_id, -assignment.awarded_points)
                assignment.awarded_points = None
        await self.challenge_junior_repo.session.flush()

    async def skip_unfinished_for_challenge(self, challenge_id: int) -> None:
        """Auto-set SKIPPED for juniors still in GOING/IN_PROGRESS when challenge completes."""
        from app.core.enums import ChallengeJuniorProgress
        assignments = await self.challenge_junior_repo.get_all_by_challenge_id(challenge_id)
        for assignment in assignments:
            if assignment.progress in (ChallengeJuniorProgress.GOING, ChallengeJuniorProgress.IN_PROGRESS):
                assignment.progress = ChallengeJuniorProgress.SKIPPED
        await self.challenge_junior_repo.session.flush()

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
