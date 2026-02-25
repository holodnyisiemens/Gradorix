from sqlalchemy import ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.schemas.enums import ChallengeJuniorProgress


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
