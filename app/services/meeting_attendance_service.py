from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.core.points_utils import recalculate_level
from app.models.meeting_attendance import MeetingAttendance
from app.repositories.meeting_attendance_repository import MeetingAttendanceRepository
from app.repositories.user_points_repository import UserPointsRepository
from app.schemas.meeting_attendance import MeetingAttendanceCreateDTO, MeetingAttendanceReadDTO, MeetingAttendanceUpdateDTO
from app.schemas.user_points import UserPointsCreateDTO, UserPointsUpdateDTO


class MeetingAttendanceService:
    def __init__(self, repo: MeetingAttendanceRepository, points_repo: UserPointsRepository):
        self.repo = repo
        self.points_repo = points_repo

    async def _get_or_404(self, attendance_id: int) -> MeetingAttendance:
        obj = await self.repo.get_by_id(attendance_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"MeetingAttendance {attendance_id} not found")
        return obj

    async def get_by_id(self, attendance_id: int) -> MeetingAttendanceReadDTO:
        return MeetingAttendanceReadDTO.model_validate(await self._get_or_404(attendance_id))

    async def get_all(
        self,
        event_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> list[MeetingAttendanceReadDTO]:
        items = await self.repo.get_all(event_id=event_id, user_id=user_id)
        return [MeetingAttendanceReadDTO.model_validate(a) for a in items]

    async def create(self, data: MeetingAttendanceCreateDTO) -> MeetingAttendanceReadDTO:
        if not data.attended:
            data = data.model_copy(update={"awarded_points": None})

        try:
            obj = await self.repo.create(data)
            if obj.attended and obj.awarded_points:
                await self._adjust_points(obj.user_id, obj.awarded_points)
            await self.repo.session.commit()
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Referenced event or user not found")
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MeetingAttendance creation error")
        return MeetingAttendanceReadDTO.model_validate(obj)

    async def update(self, attendance_id: int, data: MeetingAttendanceUpdateDTO) -> MeetingAttendanceReadDTO:
        obj = await self._get_or_404(attendance_id)
        old_awarded = obj.awarded_points or 0

        if data.attended is not None and not data.attended:
            data = data.model_copy(update={"awarded_points": None})

        try:
            obj = await self.repo.update(obj, data)

            if not obj.attended:
                if old_awarded:
                    await self._adjust_points(obj.user_id, -old_awarded)
                    obj.awarded_points = None
            else:
                new_awarded = obj.awarded_points or 0
                if new_awarded != old_awarded:
                    await self._adjust_points(obj.user_id, new_awarded - old_awarded)

            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MeetingAttendance update error")
        return MeetingAttendanceReadDTO.model_validate(obj)

    async def delete(self, attendance_id: int) -> None:
        obj = await self._get_or_404(attendance_id)
        try:
            if obj.attended and obj.awarded_points:
                await self._adjust_points(obj.user_id, -obj.awarded_points)
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MeetingAttendance delete error")

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
