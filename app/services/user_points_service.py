from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.user_points import UserPoints
from app.repositories.user_points_repository import UserPointsRepository
from app.schemas.user_points import UserPointsCreateDTO, UserPointsReadDTO, UserPointsUpdateDTO


class UserPointsService:
    def __init__(self, repo: UserPointsRepository):
        self.repo = repo

    async def _get_or_404(self, user_id: int) -> UserPoints:
        obj = await self.repo.get_by_user_id(user_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"UserPoints for user {user_id} not found")
        return obj

    async def get_by_user_id(self, user_id: int) -> UserPointsReadDTO:
        obj = await self._get_or_404(user_id)
        return UserPointsReadDTO.model_validate(obj)

    async def get_leaderboard(self) -> list[UserPointsReadDTO]:
        items = await self.repo.get_leaderboard()
        return [
            UserPointsReadDTO(
                user_id=p.user_id,
                total_points=p.total_points,
                level=p.level,
                level_name=p.level_name,
                points_to_next_level=p.points_to_next_level,
                rank=rank,
            )
            for p, rank in items
        ]

    async def create(self, data: UserPointsCreateDTO) -> UserPointsReadDTO:
        try:
            obj = await self.repo.create(data)
            await self.repo.session.commit()
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="UserPoints for this user already exist")
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="UserPoints creation error")
        return UserPointsReadDTO.model_validate(obj)

    async def update(self, user_id: int, data: UserPointsUpdateDTO) -> UserPointsReadDTO:
        obj = await self._get_or_404(user_id)
        try:
            obj = await self.repo.update(obj, data)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="UserPoints update error")
        return UserPointsReadDTO.model_validate(obj)

    async def delete(self, user_id: int) -> None:
        obj = await self._get_or_404(user_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="UserPoints delete error")
