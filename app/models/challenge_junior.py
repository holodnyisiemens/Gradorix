from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import ChallengeJuniorProgress


class ChallengeJunior(Base):
    __tablename__ = "challenge_junior"

    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"),
        primary_key=True,
    )

    junior_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    assigned_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    progress: Mapped[ChallengeJuniorProgress] = mapped_column(
        SQLEnum(ChallengeJuniorProgress, name="challenge_junior_progress"),
        nullable=False,
    )

    # Junior fills in when working on the challenge
    comment: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    links: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # list[str]

    # HR fills in when reviewing
    awarded_points: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
