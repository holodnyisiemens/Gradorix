from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import ChallengeEmployeeProgress


class ChallengeEmployee(Base):
    __tablename__ = "challenge_employee"

    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"),
        primary_key=True,
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    assigned_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    progress: Mapped[ChallengeEmployeeProgress] = mapped_column(
        SQLEnum(ChallengeEmployeeProgress, name="challenge_employee_progress"),
        nullable=False,
    )

    comment: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    links: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    awarded_points: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
