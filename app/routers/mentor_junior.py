from typing import Optional

from fastapi import APIRouter, Depends

from app.auth.utils import get_current_user, require_roles
from app.core.enums import UserRole
from app.dependencies import MentorJuniorServiceDep, NotificationServiceDep
from app.models.user import User
from app.schemas.mentor_junior import MentorJuniorCreateDTO, MentorJuniorReadDTO, MentorJuniorUpdateDTO
from app.ws.notify import push_notification

router = APIRouter(prefix="/mentor-junior", tags=["Mentor-Junior"])


@router.get("/", response_model=list[MentorJuniorReadDTO])
async def get_all(
    mentor_id: Optional[int] = None,
    junior_id: Optional[int] = None,
    service: MentorJuniorServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_all(mentor_id=mentor_id, junior_id=junior_id)


@router.get("/{mentor_id}/{junior_id}", response_model=MentorJuniorReadDTO)
async def get_by_id(
    mentor_id: int,
    junior_id: int,
    service: MentorJuniorServiceDep,
    _: User = Depends(get_current_user),
):
    return await service.get_by_id(mentor_id, junior_id)


@router.post("/", response_model=MentorJuniorReadDTO, status_code=201)
async def create(
    data: MentorJuniorCreateDTO,
    service: MentorJuniorServiceDep,
    notification_service: NotificationServiceDep,
    _: User = Depends(require_roles(UserRole.HR)),
):
    result = await service.create(data)

    try:
        await push_notification(
            data.junior_id,
            "👤 Вам назначен ментор в программе HiPo",
            notification_service,
        )
        await push_notification(
            data.mentor_id,
            "👤 К вам добавлен новый HiPo",
            notification_service,
        )
    except Exception:
        pass

    return result


@router.patch("/{mentor_id}/{junior_id}", response_model=MentorJuniorReadDTO)
async def update(
    mentor_id: int,
    junior_id: int,
    data: MentorJuniorUpdateDTO,
    service: MentorJuniorServiceDep,
    _: User = Depends(require_roles(UserRole.HR)),
):
    return await service.update(mentor_id, junior_id, data)


@router.delete("/{mentor_id}/{junior_id}", status_code=204)
async def delete(
    mentor_id: int,
    junior_id: int,
    service: MentorJuniorServiceDep,
    _: User = Depends(require_roles(UserRole.HR)),
):
    await service.delete(mentor_id, junior_id)
