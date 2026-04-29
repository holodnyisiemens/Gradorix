import datetime
from typing import Optional, List

from sqlalchemy import Date, ForeignKey, String, Text, Time, Enum as SQLEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import CalendarEventType


class CalendarEventAttendee(Base):
    __tablename__ = "calendar_event_attendees"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("calendar_events.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    start_time: Mapped[Optional[datetime.time]] = mapped_column(Time, nullable=True)

    end_time: Mapped[Optional[datetime.time]] = mapped_column(Time, nullable=True)

    event_type: Mapped[CalendarEventType] = mapped_column(
        SQLEnum(CalendarEventType, name="calendar_event_type"),
        nullable=False,
    )

    challenge_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("challenges.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    attendees: Mapped[List["CalendarEventAttendee"]] = relationship(
        "CalendarEventAttendee",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
