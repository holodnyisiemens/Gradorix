from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import hash_password
from app.models.user import User
from app.schemas.user import UserCreateDTO, UserUpdateDTO


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await self.session.get(User, user_id)

    async def create(self, user_data: UserCreateDTO) -> User:
        password_hash = hash_password(user_data.password)
        user_dict = user_data.model_dump(exclude={"password"})

        user = User(**user_dict, password_hash=password_hash)
        self.session.add(user)

        await self.session.flush()
        await self.session.refresh(user)

        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.flush()

    async def update(self, user: User, user_data: UserUpdateDTO) -> User:
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.flush()
        await self.session.refresh(user)

        return user

    async def get_all(self) -> list[User]:
        stmt = select(User)
        result = await self.session.execute(stmt)
        return result.scalars().all()
