from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.core.config import settings
from app.core.database import Base
from app.models.challenge import Challenge  # noqa
from app.models.challenge_junior import ChallengeJunior  # noqa
from app.models.mentor_junior import MentorJunior  # noqa
from app.models.notification import Notification  # noqa
from app.models.user import User  # noqa
from app.models.calendar_event import CalendarEvent  # noqa
from app.models.achievement import Achievement  # noqa
from app.models.user_achievement import UserAchievement  # noqa
from app.models.user_points import UserPoints  # noqa
from app.models.activity import Activity  # noqa
from app.models.team import Team  # noqa
from app.models.team_member import TeamMember  # noqa
from app.models.quiz import Quiz  # noqa
from app.models.quiz_result import QuizResult  # noqa
from app.models.kb_section import KBSection  # noqa
from app.models.kb_article import KBArticle  # noqa
from app.models.meeting_attendance import MeetingAttendance  # noqa
from app.models.push_subscription import PushSubscription  # noqa
from app.models.refresh_token import RefreshToken

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.database_url_psycopg)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
