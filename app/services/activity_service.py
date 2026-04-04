from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status

from app.models.activity import Activity
from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_points_repository import UserPointsRepository
from app.schemas.activity import ActivityCreateDTO, ActivityReadDTO, ActivityUpdateDTO
from app.schemas.user_points import UserPointsCreateDTO, UserPointsUpdateDTO
from app.core.enums import ActivityType, EventStatus, TaskStatus
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

    def _normalize_create_data(self, data: ActivityCreateDTO) -> None:
        if data.activity_type == ActivityType.TASK:
            if data.event_status is not None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task activity cannot have event_status")
            data.task_status = data.task_status or TaskStatus.ACTIVE
        elif data.activity_type == ActivityType.EVENT:
            if data.task_status is not None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event activity cannot have task_status")
            data.event_status = data.event_status or EventStatus.SCHEDULED
        else:
            if data.task_status is not None or data.event_status is not None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only task and event activities support status fields")

    def _validate_update_data(self, obj: Activity, data: ActivityUpdateDTO) -> None:
        if data.activity_type is not None and data.activity_type != obj.activity_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change activity type")

        if obj.activity_type == ActivityType.TASK:
            if data.event_status is not None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task activity cannot have event_status")
        elif obj.activity_type == ActivityType.EVENT:
            if data.task_status is not None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event activity cannot have task_status")
        else:
            if data.task_status is not None or data.event_status is not None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only task and event activities support status fields")

    def _status_transition_awards_points(self, obj: Activity, data: ActivityUpdateDTO) -> bool:
        if obj.activity_type == ActivityType.TASK:
            return (
                obj.task_status != TaskStatus.COMPLETED
                and data.task_status == TaskStatus.COMPLETED
                and obj.awarded_points
            )

        if obj.activity_type == ActivityType.EVENT:
            return (
                obj.event_status != EventStatus.COMPLETED
                and data.event_status == EventStatus.COMPLETED
                and obj.awarded_points
            )

        return False

    async def _award_points(self, obj: Activity) -> None:
        if not obj.user_id or not obj.awarded_points:
            return

        if obj.activity_type == ActivityType.TASK and obj.task_status != TaskStatus.COMPLETED:
            return
        if obj.activity_type == ActivityType.EVENT and obj.event_status != EventStatus.COMPLETED:
            return

        pts = await self.points_repo.get_by_user_id(obj.user_id)
        if pts:
            new_total = pts.total_points + obj.awarded_points
            level, level_name, points_to_next = recalculate_level(new_total)
            await self.points_repo.update(
                pts,
                UserPointsUpdateDTO(
                    total_points=new_total,
                    level=level,
                    level_name=level_name,
                    points_to_next_level=points_to_next,
                ),
            )
        else:
            level, level_name, points_to_next = recalculate_level(obj.awarded_points)
            await self.points_repo.create(
                UserPointsCreateDTO(
                    user_id=obj.user_id,
                    total_points=obj.awarded_points,
                    level=level,
                    level_name=level_name,
                    points_to_next_level=points_to_next,
                )
            )

    async def get_by_id(self, activity_id: int) -> ActivityReadDTO:
        return ActivityReadDTO.model_validate(await self._get_or_404(activity_id))

    async def get_all(
        self,
        user_id: Optional[int] = None,
        activity_type: Optional[ActivityType] = None,
        task_status: Optional[TaskStatus] = None,
        event_status: Optional[EventStatus] = None,
    ) -> list[ActivityReadDTO]:
        items = await self.repo.get_all(
            user_id=user_id,
            activity_type=activity_type,
            task_status=task_status,
            event_status=event_status,
        )
        return [ActivityReadDTO.model_validate(a) for a in items]

    async def create(self, data: ActivityCreateDTO) -> ActivityReadDTO:
        self._normalize_create_data(data)
        try:
            obj = await self.repo.create(data)
            await self._award_points(obj)
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
        self._validate_update_data(obj, data)
        try:
            obj = await self.repo.update(obj, data)
            if self._status_transition_awards_points(obj, data):
                await self._award_points(obj)
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
