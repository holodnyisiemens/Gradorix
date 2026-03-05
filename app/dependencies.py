from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.repositories.challenge_junior_repository import ChallengeJuniorRepository
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.mentor_junior_repository import MentorJuniorRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.services.challenge_junior_service import ChallengeJuniorService
from app.services.challenge_service import ChallengeService
from app.services.mentor_junior_service import MentorJuniorService
from app.services.notification_service import NotificationService
from app.services.user_service import UserService


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_user_service(session: SessionDep) -> UserService:
    return UserService(UserRepository(session))


def get_mentor_junior_service(session: SessionDep) -> MentorJuniorService:
    return MentorJuniorService(MentorJuniorRepository(session))


def get_notification_service(session: SessionDep) -> NotificationService:
    return NotificationService(NotificationRepository(session))


def get_challenge_service(session: SessionDep) -> ChallengeService:
    return ChallengeService(ChallengeRepository(session))


def get_challenge_junior_service(session: SessionDep) -> ChallengeJuniorService:
    return ChallengeJuniorService(ChallengeJuniorRepository(session))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
MentorJuniorServiceDep = Annotated[MentorJuniorService, Depends(get_mentor_junior_service)]
NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]
ChallengeServiceDep = Annotated[ChallengeService, Depends(get_challenge_service)]
ChallengeJuniorServiceDep = Annotated[ChallengeJuniorService, Depends(get_challenge_junior_service)]
