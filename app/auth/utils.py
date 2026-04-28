from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import secrets

from app.core.config import settings
from app.core.enums import UserRole
from app.models.user import User
from app.auth.password import hash_password, validate_password
from app.dependencies import get_session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.HASH_ALGORITHM)


def create_refresh_token() -> str:
    """Генерирует refresh токен"""
    return secrets.token_urlsafe(32)


async def store_refresh_token(user_id: int, token: str, db: AsyncSession) -> None:
    """Сохраняет refresh токен в БД"""
    from app.repositories.token_repository import TokenRepository
    repo = TokenRepository(db)
    await repo.create(user_id, token)


async def verify_refresh_token(token: str, db: AsyncSession) -> int:
    """Проверяет refresh токен и возвращает user_id"""
    from app.repositories.token_repository import TokenRepository
    repo = TokenRepository(db)
    
    refresh_token = await repo.get_by_token(token)
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    return refresh_token.user_id


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.HASH_ALGORITHM])
    except JWTError:
        raise ValueError("Invalid token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
) -> User:
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    from app.repositories.user_repository import UserRepository
    user = await UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def require_roles(*roles: UserRole):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return user

    return checker

