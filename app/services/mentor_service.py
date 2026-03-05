from app.core.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserReadDTO

from fastapi import HTTPException
from starlette import status


class MentorService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def _get_or_404(self, user_id: int) -> User:
        """Проверка существования ментора"""
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.role != UserRole.MENTOR:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mentor with ID {user_id} not found",
            )
        return user

    async def get_by_id(self, user_id: int) -> UserReadDTO:
        """Получить ментора по ID"""
        user = await self._get_or_404(user_id)
        return UserReadDTO.model_validate(user)

    async def get_all(self) -> list[UserReadDTO]:
        """Получить всех менторов"""
        users = await self.user_repo.get_all()
        return [
            UserReadDTO.model_validate(u)
            for u in users
            if u.role == UserRole.MENTOR
        ]
