from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateDTO, UserReadDTO, UserUpdateDTO


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def _get_or_404(self, user_id: int) -> User:
        """Проверка существования пользователя"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        return user

    async def _check_unique(self, field: str, value, user_id: Optional[int] = None):
        """Проверка уникальности поля"""
        existing = await self.user_repo.get_by_field(field, value)
        if existing and (user_id is None or existing.id != user_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{field.capitalize()} already exists"
            )

    async def get_by_id(self, user_id: int) -> UserReadDTO:
        """Получить пользователя по ID"""
        user = await self._get_or_404(user_id)
        return UserReadDTO.model_validate(user)

    async def create(self, user_data: UserCreateDTO) -> UserReadDTO:
        """Создать пользователя"""
        await self._check_unique("username", user_data.username)
        await self._check_unique("email", user_data.email)

        try:
            user = await self.user_repo.create(user_data)
            await self.user_repo.session.commit()
        except IntegrityError:
            await self.user_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email already exists",
            )
        except SQLAlchemyError:
            await self.user_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User creation error",
            )

        return UserReadDTO.model_validate(user)

    async def delete(self, user_id: int) -> None:
        """Удалить пользователя"""
        user = await self._get_or_404(user_id)

        try:
            await self.user_repo.delete(user)
            await self.user_repo.session.commit()
        except SQLAlchemyError:
            await self.user_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User delete error",
            )

    async def update(
        self, user_id: int, user_data: UserUpdateDTO
    ) -> UserReadDTO:
        """Обновить данные пользователя"""
        user = await self._get_or_404(user_id)

        if user_data.username is not None:
            await self._check_unique("username", user_data.username, user_id)

        if user_data.email is not None:
            await self._check_unique("email", user_data.email, user_id)

        try:
            await self.user_repo.update(user, user_data)
            await self.user_repo.session.commit()
        except IntegrityError:
            await self.user_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email already exists",
            )
        except SQLAlchemyError:
            await self.user_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="User update error",
            )

        return UserReadDTO.model_validate(user)

    async def get_all(self) -> list[UserReadDTO]:
        """Получить всех пользователей"""
        user_list = await self.user_repo.get_all()
        return [UserReadDTO.model_validate(user) for user in user_list]
    
    async def get_by_field(self, field_name: str, value) -> Optional[UserReadDTO]:
        """Получить первого пользователя, где поле field_name == value"""
        user = await self.user_repo.get_by_field(field_name, value)
        if user:
            return UserReadDTO.model_validate(user)
        return None
