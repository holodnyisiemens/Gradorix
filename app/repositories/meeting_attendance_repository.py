from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting_attendance import MeetingAttendance
from app.schemas.meeting_attendance import MeetingAttendanceCreateDTO, MeetingAttendanceUpdateDTO


class MeetingAttendanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, attendance_id: int) -> Optional[MeetingAttendance]:
        return await self.session.get(MeetingAttendance, attendance_id)

    async def create(self, data: MeetingAttendanceCreateDTO) -> MeetingAttendance:
        attendance = MeetingAttendance(**data.model_dump())
        self.session.add(attendance)
        await self.session.flush()
        await self.session.refresh(attendance)
        return attendance

    async def delete(self, attendance: MeetingAttendance) -> None:
        await self.session.delete(attendance)
        await self.session.flush()

    async def update(self, attendance: MeetingAttendance, data: MeetingAttendanceUpdateDTO) -> MeetingAttendance:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(attendance, field, value)
        await self.session.flush()
        await self.session.refresh(attendance)
        return attendance

    async def get_all(
        self,
        activity_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> list[MeetingAttendance]:
        stmt = select(MeetingAttendance)
        if activity_id is not None:
            stmt = stmt.where(MeetingAttendance.activity_id == activity_id)
        if user_id is not None:
            stmt = stmt.where(MeetingAttendance.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
