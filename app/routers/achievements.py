from fastapi import APIRouter

from app.dependencies import AchievementServiceDep
from app.schemas.achievement import AchievementCreateDTO, AchievementReadDTO, AchievementUpdateDTO

router = APIRouter(prefix="/achievements", tags=["Achievements"])


@router.get("/", response_model=list[AchievementReadDTO])
async def get_all(service: AchievementServiceDep = ...):
    return await service.get_all()


@router.get("/{achievement_id}", response_model=AchievementReadDTO)
async def get_by_id(achievement_id: int, service: AchievementServiceDep = ...):
    return await service.get_by_id(achievement_id)


@router.post("/", response_model=AchievementReadDTO, status_code=201)
async def create(data: AchievementCreateDTO, service: AchievementServiceDep = ...):
    return await service.create(data)


@router.patch("/{achievement_id}", response_model=AchievementReadDTO)
async def update(achievement_id: int, data: AchievementUpdateDTO, service: AchievementServiceDep = ...):
    return await service.update(achievement_id, data)


@router.delete("/{achievement_id}", status_code=204)
async def delete(achievement_id: int, service: AchievementServiceDep = ...):
    await service.delete(achievement_id)
