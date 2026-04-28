from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class TokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, token: str) -> RefreshToken:
        """Создать refresh токен"""
        refresh_token = RefreshToken(user_id=user_id, token=token)
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Получить refresh токен по значению"""
        query = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_by_token(self, token: str) -> None:
        """Удалить refresh токен"""
        query = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.session.execute(query)
        refresh_token = result.scalar_one_or_none()
        if refresh_token:
            await self.session.delete(refresh_token)

    async def delete_by_user_id(self, user_id: int) -> None:
        """Удалить все refresh токены пользователя"""
        query = select(RefreshToken).where(RefreshToken.user_id == user_id)
        result = await self.session.execute(query)
        tokens = result.scalars().all()
        for token in tokens:
            await self.session.delete(token)
