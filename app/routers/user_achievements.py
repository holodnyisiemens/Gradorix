from typing import Optional

from fastapi import APIRouter

from app.dependencies import UserAchievementServiceDep
from app.schemas.user_achievement import UserAchievementCreateDTO, UserAchievementReadDTO, UserAchievementUpdateDTO

router = APIRouter(prefix="/user-achievements", tags=["User Achievements"])


@router.get("/", response_model=list[UserAchievementReadDTO])
async def get_all(user_id: Optional[int] = None, service: UserAchievementServiceDep = ...):
    return await service.get_all(user_id=user_id)


@router.get("/{user_id}/{achievement_id}", response_model=UserAchievementReadDTO)
async def get_by_id(user_id: int, achievement_id: int, service: UserAchievementServiceDep = ...):
    return await service.get_by_id(user_id, achievement_id)


@router.post("/", response_model=UserAchievementReadDTO, status_code=201)
async def create(data: UserAchievementCreateDTO, service: UserAchievementServiceDep = ...):
    return await service.create(data)


@router.patch("/{user_id}/{achievement_id}", response_model=UserAchievementReadDTO)
async def update(user_id: int, achievement_id: int, data: UserAchievementUpdateDTO, service: UserAchievementServiceDep = ...):
    return await service.update(user_id, achievement_id, data)


@router.delete("/{user_id}/{achievement_id}", status_code=204)
async def delete(user_id: int, achievement_id: int, service: UserAchievementServiceDep = ...):
    await service.delete(user_id, achievement_id)
