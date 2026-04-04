from typing import Optional

from fastapi import APIRouter

from app.dependencies import MeetingAttendanceServiceDep
from app.schemas.meeting_attendance import MeetingAttendanceCreateDTO, MeetingAttendanceReadDTO, MeetingAttendanceUpdateDTO

router = APIRouter(prefix="/meeting-attendance", tags=["Meeting Attendance"])


@router.get("/", response_model=list[MeetingAttendanceReadDTO])
async def get_all(
    activity_id: Optional[int] = None,
    user_id: Optional[int] = None,
    service: MeetingAttendanceServiceDep = ...,
):
    return await service.get_all(activity_id=activity_id, user_id=user_id)


@router.get("/{attendance_id}", response_model=MeetingAttendanceReadDTO)
async def get_by_id(attendance_id: int, service: MeetingAttendanceServiceDep = ...):
    return await service.get_by_id(attendance_id)


@router.post("/", response_model=MeetingAttendanceReadDTO, status_code=201)
async def create(data: MeetingAttendanceCreateDTO, service: MeetingAttendanceServiceDep = ...):
    return await service.create(data)


@router.patch("/{attendance_id}", response_model=MeetingAttendanceReadDTO)
async def update(attendance_id: int, data: MeetingAttendanceUpdateDTO, service: MeetingAttendanceServiceDep = ...):
    return await service.update(attendance_id, data)


@router.delete("/{attendance_id}", status_code=204)
async def delete(attendance_id: int, service: MeetingAttendanceServiceDep = ...):
    await service.delete(attendance_id)
