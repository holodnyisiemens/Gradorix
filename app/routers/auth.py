from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import UserServiceDep, get_session
from app.schemas.user import UserCreateDTO, UserLogin
from app.schemas.token import TokenResponse, RefreshTokenRequest
from app.auth.utils import (
    create_access_token,
    create_refresh_token,
    store_refresh_token,
    verify_refresh_token,
    validate_password,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201, response_model=TokenResponse)
async def register(
    data: UserCreateDTO,
    service: UserServiceDep,
    db: AsyncSession = Depends(get_session)
):
    user = await service.create(data)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token()
    
    await store_refresh_token(user.id, refresh_token, db)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    service: UserServiceDep,
    db: AsyncSession = Depends(get_session)
):
    user = await service.get_by_username(data.username)

    if not user:
        raise HTTPException(401, "Invalid credentials")

    if not validate_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token()
    
    await store_refresh_token(user.id, refresh_token, db)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_session)
):
    """Обновляет access токен используя refresh токен"""
    try:
        user_id = await verify_refresh_token(data.refresh_token, db)
    except HTTPException:
        raise
    
    access_token = create_access_token(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": data.refresh_token,
    }
