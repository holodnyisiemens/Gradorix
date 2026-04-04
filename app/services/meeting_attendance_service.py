from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.activity import Activity
from app.models.meeting_attendance import MeetingAttendance
from app.repositories.activity_repository import ActivityRepository
from app.repositories.meeting_attendance_repository import MeetingAttendanceRepository
from app.schemas.meeting_attendance import MeetingAttendanceCreateDTO, MeetingAttendanceReadDTO, MeetingAttendanceUpdateDTO
from app.core.enums import ActivityType


class MeetingAttendanceService:
    def __init__(self, repo: MeetingAttendanceRepository, activity_repo: ActivityRepository):
        self.repo = repo
        self.activity_repo = activity_repo

    async def _validate_activity_is_event(self, activity_id: int) -> Activity:
        """Verify that activity exists and is of type EVENT"""
        activity = await self.activity_repo.get_by_id(activity_id)
        if not activity or activity.activity_type != ActivityType.EVENT:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event activity with ID {activity_id} not found",
            )
        return activity

    async def _get_or_404(self, attendance_id: int) -> MeetingAttendance:
        obj = await self.repo.get_by_id(attendance_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"MeetingAttendance {attendance_id} not found")
        return obj

    async def get_by_id(self, attendance_id: int) -> MeetingAttendanceReadDTO:
        return MeetingAttendanceReadDTO.model_validate(await self._get_or_404(attendance_id))

    async def get_all(
        self,
        activity_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> list[MeetingAttendanceReadDTO]:
        items = await self.repo.get_all(activity_id=activity_id, user_id=user_id)
        return [MeetingAttendanceReadDTO.model_validate(a) for a in items]

    async def create(self, data: MeetingAttendanceCreateDTO) -> MeetingAttendanceReadDTO:
        await self._validate_activity_is_event(data.activity_id)
        try:
            obj = await self.repo.create(data)
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
        try:
            obj = await self.repo.update(obj, data)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MeetingAttendance update error")
        return MeetingAttendanceReadDTO.model_validate(obj)

    async def delete(self, attendance_id: int) -> None:
        obj = await self._get_or_404(attendance_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MeetingAttendance delete error")
