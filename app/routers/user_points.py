from fastapi import APIRouter

from app.dependencies import UserPointsServiceDep
from app.schemas.user_points import UserPointsCreateDTO, UserPointsReadDTO, UserPointsUpdateDTO

router = APIRouter(prefix="/user-points", tags=["User Points"])


@router.get("/leaderboard", response_model=list[UserPointsReadDTO])
async def get_leaderboard(service: UserPointsServiceDep = ...):
    return await service.get_leaderboard()


@router.get("/{user_id}", response_model=UserPointsReadDTO)
async def get_by_user_id(user_id: int, service: UserPointsServiceDep = ...):
    return await service.get_by_user_id(user_id)


@router.post("/", response_model=UserPointsReadDTO, status_code=201)
async def create(data: UserPointsCreateDTO, service: UserPointsServiceDep = ...):
    return await service.create(data)


@router.patch("/{user_id}", response_model=UserPointsReadDTO)
async def update(user_id: int, data: UserPointsUpdateDTO, service: UserPointsServiceDep = ...):
    return await service.update(user_id, data)


@router.delete("/{user_id}", status_code=204)
async def delete(user_id: int, service: UserPointsServiceDep = ...):
    await service.delete(user_id)
