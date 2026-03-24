from typing import Optional

from sqlalchemy import ForeignKey, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import TeamStatus


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    project: Mapped[str] = mapped_column(String(255), nullable=False)

    status: Mapped[TeamStatus] = mapped_column(
        SQLEnum(TeamStatus, name="team_status"),
        nullable=False,
        default=TeamStatus.ACTIVE,
    )

    mentor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
