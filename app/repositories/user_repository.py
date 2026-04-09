from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.password import hash_password
from app.models.user import User
from app.schemas.user import UserCreateDTO, UserUpdateDTO


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return await self.session.get(User, user_id)

    async def create(self, user_data: UserCreateDTO) -> User:
        """Создать пользователя"""
        password_hash = hash_password(user_data.password)
        user_dict = user_data.model_dump(exclude={"password"})

        user = User(**user_dict, password_hash=password_hash)
        self.session.add(user)

        await self.session.flush()
        await self.session.refresh(user)

        return user

    async def delete(self, user: User) -> None:
        """Удалить пользователя"""
        await self.session.delete(user)
        await self.session.flush()

    async def update(self, user: User, user_data: UserUpdateDTO) -> User:
        """Обновить данные пользователя"""
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.flush()
        await self.session.refresh(user)

        return user

    async def get_all(self) -> list[User]:
        """Получить всех пользователей"""
        stmt = select(User)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_by_role(self, role: str) -> list[User]:
        """Получить всех пользователей с заданной ролью"""
        stmt = select(User).where(User.role == role)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_field(self, field_name: str, value) -> Optional[User]:
        """Получить первого пользователя, где поле field_name == value"""
        column = getattr(User, field_name)
        stmt = select(User).where(column == value)
        result = await self.session.execute(stmt)
        return result.scalars().first()
