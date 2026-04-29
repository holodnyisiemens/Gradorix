from typing import Optional

from fastapi import APIRouter, Depends

from app.auth.utils import get_current_user, require_roles
from app.core.enums import UserRole
from app.dependencies import MentorEmployeeServiceDep, NotificationServiceDep
from app.models.user import User
from app.schemas.mentor_employee import MentorEmployeeCreateDTO, MentorEmployeeReadDTO, MentorEmployeeUpdateDTO
from app.ws.notify import push_notification

router = APIRouter(prefix="/mentor-employee", tags=["Mentor-Employee"])


@router.get("/", response_model=list[MentorEmployeeReadDTO])
async def get_all(
    mentor_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    service: MentorEmployeeServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_all(mentor_id=mentor_id, employee_id=employee_id)


@router.get("/{mentor_id}/{employee_id}", response_model=MentorEmployeeReadDTO)
async def get_by_id(
    mentor_id: int,
    employee_id: int,
    service: MentorEmployeeServiceDep,
    _: User = Depends(get_current_user),
):
    return await service.get_by_id(mentor_id, employee_id)


@router.post("/", response_model=MentorEmployeeReadDTO, status_code=201)
async def create(
    data: MentorEmployeeCreateDTO,
    service: MentorEmployeeServiceDep,
    notification_service: NotificationServiceDep,
    _: User = Depends(require_roles(UserRole.HR)),
):
    result = await service.create(data)
    try:
        await push_notification(
            data.employee_id,
            "👤 Вам назначен ментор в программе развития",
            notification_service,
        )
        await push_notification(
            data.mentor_id,
            "👤 К вам добавлен новый сотрудник",
            notification_service,
        )
    except Exception:
        pass
    return result


@router.patch("/{mentor_id}/{employee_id}", response_model=MentorEmployeeReadDTO)
async def update(
    mentor_id: int,
    employee_id: int,
    data: MentorEmployeeUpdateDTO,
    service: MentorEmployeeServiceDep,
    _: User = Depends(require_roles(UserRole.HR)),
):
    return await service.update(mentor_id, employee_id, data)


@router.delete("/{mentor_id}/{employee_id}", status_code=204)
async def delete(
    mentor_id: int,
    employee_id: int,
    service: MentorEmployeeServiceDep,
    _: User = Depends(require_roles(UserRole.HR)),
):
    await service.delete(mentor_id, employee_id)
