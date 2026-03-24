from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationCreateDTO, NotificationReadDTO, NotificationUpdateDTO


class NotificationService:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo

    async def _get_or_404(self, notification_id: int) -> Notification:
        """Проверка существования уведомления"""
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification with ID {notification_id} not found",
            )
        return notification

    async def get_by_id(self, notification_id: int) -> NotificationReadDTO:
        """Получить уведомление по ID"""
        notification = await self._get_or_404(notification_id)
        return NotificationReadDTO.model_validate(notification)

    async def create(self, data: NotificationCreateDTO) -> NotificationReadDTO:
        """Создать уведомление"""
        try:
            notification = await self.notification_repo.create(data)
            await self.notification_repo.session.commit()
        except IntegrityError:
            await self.notification_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Referenced user not found",
            )
        except SQLAlchemyError:
            await self.notification_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Notification creation error",
            )

        return NotificationReadDTO.model_validate(notification)

    async def delete(self, notification_id: int) -> None:
        """Удалить уведомление"""
        notification = await self._get_or_404(notification_id)

        try:
            await self.notification_repo.delete(notification)
            await self.notification_repo.session.commit()
        except SQLAlchemyError:
            await self.notification_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Notification delete error",
            )

    async def update(
        self, notification_id: int, data: NotificationUpdateDTO
    ) -> NotificationReadDTO:
        """Обновить уведомление"""
        notification = await self._get_or_404(notification_id)

        try:
            notification = await self.notification_repo.update(notification, data)
            await self.notification_repo.session.commit()
        except IntegrityError:
            await self.notification_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Referenced user not found",
            )
        except SQLAlchemyError:
            await self.notification_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Notification update error",
            )

        return NotificationReadDTO.model_validate(notification)

    async def get_all(self, user_id: Optional[int] = None) -> list[NotificationReadDTO]:
        """Получить все уведомления, опционально — по пользователю"""
        notifications = await self.notification_repo.get_all(user_id=user_id)
        return [NotificationReadDTO.model_validate(n) for n in notifications]
