from fastapi import APIRouter

from app.dependencies import UserServiceDep
from app.schemas.user import UserCreateDTO, UserReadDTO, UserUpdateDTO

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserReadDTO])
async def get_all_users(service: UserServiceDep):
    return await service.get_all()


@router.get("/{user_id}", response_model=UserReadDTO)
async def get_user(user_id: int, service: UserServiceDep):
    return await service.get_by_id(user_id)


@router.post("/", response_model=UserReadDTO, status_code=201)
async def create_user(data: UserCreateDTO, service: UserServiceDep):
    return await service.create(data)


@router.patch("/{user_id}", response_model=UserReadDTO)
async def update_user(user_id: int, data: UserUpdateDTO, service: UserServiceDep):
    return await service.update(user_id, data)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, service: UserServiceDep):
    await service.delete(user_id)
