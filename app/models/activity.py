import datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import ActivityType, CalendarEventType, EventStatus, TaskStatus


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    requested_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    awarded_points: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    task_status: Mapped[Optional[TaskStatus]] = mapped_column(
        SQLEnum(TaskStatus, name="task_status"),
        nullable=True,
    )

    event_status: Mapped[Optional[EventStatus]] = mapped_column(
        SQLEnum(EventStatus, name="event_status"),
        nullable=True,
    )

    activity_type: Mapped[ActivityType] = mapped_column(
        SQLEnum(ActivityType, name="activity_type"),
        nullable=False,
    )

    date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)

    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    event_type: Mapped[Optional[CalendarEventType]] = mapped_column(
        SQLEnum(CalendarEventType, name="event_type"),
        nullable=True,
    )

    challenge_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

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
