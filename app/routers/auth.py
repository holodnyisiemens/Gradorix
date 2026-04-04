from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import UserServiceDep
from app.schemas.user import UserCreateDTO, UserLogin
from app.schemas.token import TokenResponse
from app.auth.utils import create_access_token, hash_password, validate_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201, response_model=TokenResponse)
async def register(
    data: UserCreateDTO,
    service: UserServiceDep
):

    user = await service.create(data)

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
    }

    # return {"message": f"User {user.username} created"}


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    service: UserServiceDep
):
    user = await service.get_by_email(data.email)

    if not user:
        raise HTTPException(401, "Invalid credentials")

    if not validate_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
    }

