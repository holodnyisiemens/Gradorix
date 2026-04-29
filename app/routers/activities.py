from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from starlette import status as http_status

from app.auth.utils import get_current_user, require_roles
from app.core.enums import ActivityStatus, UserRole
from app.dependencies import ActivityServiceDep
from app.models.user import User
from app.schemas.activity import ActivityCreateDTO, ActivityReadDTO, ActivityUpdateDTO

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("/", response_model=list[ActivityReadDTO])
async def get_all(
    user_id: Optional[int] = None,
    activity_status: Optional[ActivityStatus] = None,
    service: ActivityServiceDep = ...,
    current_user: User = Depends(get_current_user),
):
    # JUNIOR sees only their own activities
    if current_user.role == UserRole.EMPLOYEE:
        user_id = current_user.id
    return await service.get_all(user_id=user_id, activity_status=activity_status)


@router.get("/{activity_id}", response_model=ActivityReadDTO)
async def get_by_id(
    activity_id: int,
    service: ActivityServiceDep = ...,
    current_user: User = Depends(get_current_user),
):
    activity = await service.get_by_id(activity_id)
    if current_user.role == UserRole.EMPLOYEE and activity.user_id != current_user.id:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return activity


@router.post("/", response_model=ActivityReadDTO, status_code=201)
async def create(
    data: ActivityCreateDTO,
    service: ActivityServiceDep = ...,
    current_user: User = Depends(get_current_user),
):
    # JUNIOR can only submit for themselves
    if current_user.role == UserRole.EMPLOYEE:
        data = data.model_copy(update={"user_id": current_user.id, "requested_points": 0})
    return await service.create(data)


@router.patch("/{activity_id}", response_model=ActivityReadDTO)
async def update(
    activity_id: int,
    data: ActivityUpdateDTO,
    service: ActivityServiceDep = ...,
    current_user: User = Depends(get_current_user),
):
    activity = await service.get_by_id(activity_id)

    if current_user.role == UserRole.EMPLOYEE:
        # JUNIOR can only edit their own pending activities (title, description, links, achieved_date)
        if activity.user_id != current_user.id:
            raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Forbidden")
        if activity.status != ActivityStatus.PENDING:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail="Cannot edit activity that is no longer pending",
            )
        # Strip HR-only fields
        data = data.model_copy(update={"awarded_points": None, "status": None, "review_note": None, "reviewed_at": None})

    return await service.update(activity_id, data)


@router.delete("/{activity_id}", status_code=204)
async def delete(
    activity_id: int,
    service: ActivityServiceDep = ...,
    current_user: User = Depends(get_current_user),
):
    activity = await service.get_by_id(activity_id)
    if current_user.role == UserRole.EMPLOYEE and activity.user_id != current_user.id:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Forbidden")
    await service.delete(activity_id)
