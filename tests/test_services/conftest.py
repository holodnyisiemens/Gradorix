import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole, ChallengeEmployeeProgress
from app.repositories.challenge_employee_repository import ChallengeEmployeeRepository
from app.repositories.mentor_employee_repository import MentorEmployeeRepository
from app.schemas.challenge_employee import ChallengeEmployeeCreateDTO
from app.schemas.mentor_employee import MentorEmployeeCreateDTO
from app.schemas.user import UserCreateDTO
from app.services.challenge_employee_service import ChallengeEmployeeService
from app.services.challenge_service import ChallengeService
from app.services.mentor_employee_service import MentorEmployeeService
from app.services.mentor_service import MentorService
from app.services.notification_service import NotificationService
from app.services.user_service import UserService


@pytest.fixture
def mentor_employee_repository(session: AsyncSession) -> MentorEmployeeRepository:
    return MentorEmployeeRepository(session)


@pytest.fixture
def challenge_employee_repository(session: AsyncSession) -> ChallengeEmployeeRepository:
    return ChallengeEmployeeRepository(session)


@pytest.fixture
def user_service(user_repository) -> UserService:
    return UserService(user_repository)


@pytest.fixture
def mentor_service(user_repository) -> MentorService:
    return MentorService(user_repository)


@pytest.fixture
def mentor_employee_service(mentor_employee_repository) -> MentorEmployeeService:
    return MentorEmployeeService(mentor_employee_repository)


@pytest.fixture
def notification_service(notification_repository) -> NotificationService:
    return NotificationService(notification_repository)


@pytest.fixture
def challenge_service(challenge_repository) -> ChallengeService:
    return ChallengeService(challenge_repository)


@pytest.fixture
def challenge_employee_service(challenge_employee_repository) -> ChallengeEmployeeService:
    return ChallengeEmployeeService(challenge_employee_repository, None)


@pytest.fixture
def mentor_users() -> list[UserCreateDTO]:
    return [
        UserCreateDTO(username="mentor1", password="123456", role=UserRole.MENTOR),
        UserCreateDTO(username="mentor2", password="123456", role=UserRole.MENTOR),
    ]


@pytest.fixture
def mentor_employee_data() -> list[MentorEmployeeCreateDTO]:
    return []


@pytest.fixture
def challenge_employee_data() -> list[ChallengeEmployeeCreateDTO]:
    return []
