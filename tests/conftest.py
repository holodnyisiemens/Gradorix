import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.database import Base
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.challenge import ChallengeCreateDTO
from app.core.enums import UserRole
from app.schemas.notification import NotificationCreateDTO
from app.schemas.user import UserCreateDTO


TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD.get_secret_value()}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/test_gradorix"
)


@pytest.fixture()
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest.fixture(autouse=True)
async def setup_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def session(engine):
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
def user_repository(session) -> UserRepository:
    return UserRepository(session)


@pytest.fixture
def notification_repository(session) -> NotificationRepository:
    return NotificationRepository(session)


@pytest.fixture
def challenge_repository(session) -> ChallengeRepository:
    return ChallengeRepository(session)


@pytest.fixture
def users() -> list[UserCreateDTO]:
    users = [
        UserCreateDTO(
            username="alexey",
            password="123456",
            role=UserRole.HR,
        ),
        UserCreateDTO(
            username="alexander",
            password="123456",
            role=UserRole.EMPLOYEE,
        ),
    ]
    return users


@pytest.fixture
def notifications() -> list[NotificationCreateDTO]:
    notifications = [
        NotificationCreateDTO(
            user_id=1,
            message="Take the test",
        ),
        NotificationCreateDTO(
            user_id=1,
            message="The event is coming soon",
            is_read=True,
        ),
    ]
    return notifications


@pytest.fixture
def challenges() -> list[ChallengeCreateDTO]:
    challenges = [
        ChallengeCreateDTO(
            title="New test",
            status="ACTIVE",
        ),
        ChallengeCreateDTO(
            title="New event",
            status="DRAFT",
        ),
    ]
    return challenges
