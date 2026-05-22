from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.auth.utils import get_current_user
from app.core.enums import UserRole
from app.dependencies import MeetingAttendanceServiceDep
from app.models.user import User
from app.schemas.meeting_attendance import MeetingAttendanceCreateDTO, MeetingAttendanceReadDTO, MeetingAttendanceUpdateDTO

router = APIRouter(prefix="/meeting-attendance", tags=["Meeting Attendance"])


@router.get("/", response_model=list[MeetingAttendanceReadDTO])
async def get_all(
    event_id: Optional[int] = None,
    user_id: Optional[int] = None,
    service: MeetingAttendanceServiceDep = ...,
):
    return await service.get_all(event_id=event_id, user_id=user_id)


@router.get("/{attendance_id}", response_model=MeetingAttendanceReadDTO)
async def get_by_id(attendance_id: int, service: MeetingAttendanceServiceDep = ...):
    return await service.get_by_id(attendance_id)


@router.post("/", response_model=MeetingAttendanceReadDTO, status_code=201)
async def create(
    data: MeetingAttendanceCreateDTO,
    service: MeetingAttendanceServiceDep = ...,
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.HR and data.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    if current_user.role != UserRole.HR or data.user_id == current_user.id:
        data = data.model_copy(update={"awarded_points": None})

    return await service.create(data)


@router.patch("/{attendance_id}", response_model=MeetingAttendanceReadDTO)
async def update(
    attendance_id: int,
    data: MeetingAttendanceUpdateDTO,
    service: MeetingAttendanceServiceDep = ...,
    current_user: User = Depends(get_current_user),
):
    attendance = await service.get_by_id(attendance_id)
    if current_user.role != UserRole.HR and attendance.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    if current_user.role != UserRole.HR or attendance.user_id == current_user.id:
        data = data.model_copy(update={"awarded_points": None})

    return await service.update(attendance_id, data)


@router.delete("/{attendance_id}", status_code=204)
async def delete(attendance_id: int, service: MeetingAttendanceServiceDep = ...):
    await service.delete(attendance_id)
