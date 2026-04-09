import datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Enum as SQLEnum, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import ActivityStatus, ActivityType


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str] = mapped_column(String(1000), nullable=False)

    requested_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    awarded_points: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    status: Mapped[ActivityStatus] = mapped_column(
        SQLEnum(ActivityStatus, name="activity_status"),
        nullable=False,
        default=ActivityStatus.PENDING,
    )

    activity_type: Mapped[ActivityType] = mapped_column(
        SQLEnum(ActivityType, name="activity_type"),
        nullable=False,
    )

    submitted_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    reviewed_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    review_note: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Supporting URLs (e.g. conference page, certificate)
    links: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # list[str]

    # Date when the activity actually happened (may differ from submission date)
    achieved_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
