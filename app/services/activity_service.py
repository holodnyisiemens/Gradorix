from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.activity import Activity
from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_points_repository import UserPointsRepository
from app.schemas.activity import ActivityCreateDTO, ActivityReadDTO, ActivityUpdateDTO
from app.schemas.user_points import UserPointsCreateDTO, UserPointsUpdateDTO
from app.core.enums import ActivityStatus
from app.core.points_utils import recalculate_level


class ActivityService:
    def __init__(self, repo: ActivityRepository, points_repo: UserPointsRepository):
        self.repo = repo
        self.points_repo = points_repo

    async def _get_or_404(self, activity_id: int) -> Activity:
        obj = await self.repo.get_by_id(activity_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Activity {activity_id} not found")
        return obj

    async def get_by_id(self, activity_id: int) -> ActivityReadDTO:
        return ActivityReadDTO.model_validate(await self._get_or_404(activity_id))

    async def get_all(
        self,
        user_id: Optional[int] = None,
        activity_status: Optional[ActivityStatus] = None,
    ) -> list[ActivityReadDTO]:
        items = await self.repo.get_all(user_id=user_id, status=activity_status)
        return [ActivityReadDTO.model_validate(a) for a in items]

    async def create(self, data: ActivityCreateDTO) -> ActivityReadDTO:
        try:
            obj = await self.repo.create(data)
            await self.repo.session.commit()
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Referenced user not found")
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Activity creation error")
        return ActivityReadDTO.model_validate(obj)

    async def update(self, activity_id: int, data: ActivityUpdateDTO) -> ActivityReadDTO:
        obj = await self._get_or_404(activity_id)
        was_approved = obj.status == ActivityStatus.APPROVED
        try:
            obj = await self.repo.update(obj, data)

            # Add points when activity is approved (only once — not if it was already approved)
            newly_approved = (
                not was_approved
                and data.status == ActivityStatus.APPROVED
                and obj.awarded_points
            )
            if newly_approved:
                pts = await self.points_repo.get_by_user_id(obj.user_id)
                if pts:
                    new_total = pts.total_points + obj.awarded_points
                    level, level_name, points_to_next = recalculate_level(new_total)
                    await self.points_repo.update(pts, UserPointsUpdateDTO(
                        total_points=new_total,
                        level=level,
                        level_name=level_name,
                        points_to_next_level=points_to_next,
                    ))
                else:
                    level, level_name, points_to_next = recalculate_level(obj.awarded_points)
                    await self.points_repo.create(UserPointsCreateDTO(
                        user_id=obj.user_id,
                        total_points=obj.awarded_points,
                        level=level,
                        level_name=level_name,
                        points_to_next_level=points_to_next,
                    ))

            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Activity update error")
        return ActivityReadDTO.model_validate(obj)

    async def delete(self, activity_id: int) -> None:
        obj = await self._get_or_404(activity_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Activity delete error")
