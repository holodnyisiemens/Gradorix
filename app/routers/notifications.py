from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.utils import get_current_user, require_roles
from app.core.enums import UserRole
from app.dependencies import NotificationServiceDep
from app.models.user import User
from app.schemas.notification import NotificationCreateDTO, NotificationReadDTO, NotificationUpdateDTO
from app.ws.notify import push_ws_only

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=list[NotificationReadDTO])
async def get_all(
    user_id: Optional[int] = None,
    service: NotificationServiceDep = ...,
    current_user: User = Depends(get_current_user),
):
    # HR may query any user's notifications; others only see their own
    if current_user.role == UserRole.HR:
        return await service.get_all(user_id=user_id)
    return await service.get_all(user_id=current_user.id)


@router.get("/{notification_id}", response_model=NotificationReadDTO)
async def get_by_id(
    notification_id: int,
    service: NotificationServiceDep,
    current_user: User = Depends(get_current_user),
):
    notification = await service.get_by_id(notification_id)
    if current_user.role != UserRole.HR and notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return notification


@router.post("/", response_model=NotificationReadDTO, status_code=201)
async def create(
    data: NotificationCreateDTO,
    service: NotificationServiceDep,
    _: User = Depends(require_roles(UserRole.HR, UserRole.MENTOR)),
):
    notification = await service.create(data)
    await push_ws_only(notification)
    return notification


@router.patch("/{notification_id}", response_model=NotificationReadDTO)
async def update(
    notification_id: int,
    data: NotificationUpdateDTO,
    service: NotificationServiceDep,
    current_user: User = Depends(get_current_user),
):
    notification = await service.get_by_id(notification_id)
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    # Prevent ownership reassignment via PATCH
    if data.user_id is not None and data.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot reassign notification ownership")
    return await service.update(notification_id, data)


@router.delete("/{notification_id}", status_code=204)
async def delete(
    notification_id: int,
    service: NotificationServiceDep,
    current_user: User = Depends(get_current_user),
):
    notification = await service.get_by_id(notification_id)
    if current_user.role != UserRole.HR and notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    await service.delete(notification_id)
