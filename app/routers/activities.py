from typing import Optional

from fastapi import APIRouter

from app.dependencies import ActivityServiceDep
from app.schemas.activity import ActivityCreateDTO, ActivityReadDTO, ActivityUpdateDTO
from app.core.enums import ActivityStatus

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("/", response_model=list[ActivityReadDTO])
async def get_all(
    user_id: Optional[int] = None,
    activity_status: Optional[ActivityStatus] = None,
    service: ActivityServiceDep = ...,
):
    return await service.get_all(user_id=user_id, activity_status=activity_status)


@router.get("/{activity_id}", response_model=ActivityReadDTO)
async def get_by_id(activity_id: int, service: ActivityServiceDep = ...):
    return await service.get_by_id(activity_id)


@router.post("/", response_model=ActivityReadDTO, status_code=201)
async def create(data: ActivityCreateDTO, service: ActivityServiceDep = ...):
    return await service.create(data)


@router.patch("/{activity_id}", response_model=ActivityReadDTO)
async def update(activity_id: int, data: ActivityUpdateDTO, service: ActivityServiceDep = ...):
    return await service.update(activity_id, data)


@router.delete("/{activity_id}", status_code=204)
async def delete(activity_id: int, service: ActivityServiceDep = ...):
    await service.delete(activity_id)
