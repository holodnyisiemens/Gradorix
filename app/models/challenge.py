import datetime
from typing import Optional

from sqlalchemy import Date, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import ChallengeStatus


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    status: Mapped[ChallengeStatus] = mapped_column(SQLEnum(ChallengeStatus, name="challenge_status"), nullable=False)

    date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)

    max_points: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
