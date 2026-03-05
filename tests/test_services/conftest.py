import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole, ChallengeJuniorProgress
from app.repositories.challenge_junior_repository import ChallengeJuniorRepository
from app.repositories.mentor_junior_repository import MentorJuniorRepository
from app.schemas.challenge_junior import ChallengeJuniorCreateDTO
from app.schemas.mentor_junior import MentorJuniorCreateDTO
from app.schemas.user import UserCreateDTO
from app.services.challenge_junior_service import ChallengeJuniorService
from app.services.challenge_service import ChallengeService
from app.services.mentor_junior_service import MentorJuniorService
from app.services.mentor_service import MentorService
from app.services.notification_service import NotificationService
from app.services.user_service import UserService


@pytest.fixture
def mentor_junior_repository(session: AsyncSession) -> MentorJuniorRepository:
    return MentorJuniorRepository(session)


@pytest.fixture
def challenge_junior_repository(session: AsyncSession) -> ChallengeJuniorRepository:
    return ChallengeJuniorRepository(session)


@pytest.fixture
def user_service(user_repository) -> UserService:
    return UserService(user_repository)


@pytest.fixture
def mentor_service(user_repository) -> MentorService:
    return MentorService(user_repository)


@pytest.fixture
def mentor_junior_service(mentor_junior_repository) -> MentorJuniorService:
    return MentorJuniorService(mentor_junior_repository)


@pytest.fixture
def notification_service(notification_repository) -> NotificationService:
    return NotificationService(notification_repository)


@pytest.fixture
def challenge_service(challenge_repository) -> ChallengeService:
    return ChallengeService(challenge_repository)


@pytest.fixture
def challenge_junior_service(challenge_junior_repository) -> ChallengeJuniorService:
    return ChallengeJuniorService(challenge_junior_repository)


@pytest.fixture
def mentor_users() -> list[UserCreateDTO]:
    return [
        UserCreateDTO(
            username="mentor1",
            email="mentor1@example.com",
            password="123456",
            role=UserRole.MENTOR,
        ),
        UserCreateDTO(
            username="mentor2",
            email="mentor2@example.com",
            password="123456",
            role=UserRole.MENTOR,
        ),
    ]


@pytest.fixture
def mentor_junior_data() -> list[MentorJuniorCreateDTO]:
    """IDs подставляются в тестах после создания пользователей"""
    return []


@pytest.fixture
def challenge_junior_data() -> list[ChallengeJuniorCreateDTO]:
    """IDs подставляются в тестах после создания сущностей"""
    return []
