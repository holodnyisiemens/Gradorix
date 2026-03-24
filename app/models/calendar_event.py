import datetime
from typing import Optional

from sqlalchemy import Date, ForeignKey, String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import CalendarEventType


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    event_type: Mapped[CalendarEventType] = mapped_column(
        SQLEnum(CalendarEventType, name="calendar_event_type"),
        nullable=False,
    )

    challenge_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("challenges.id", ondelete="SET NULL"),
        nullable=True,
    )

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
