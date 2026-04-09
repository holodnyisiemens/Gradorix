import datetime
from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class QuizResult(Base):
    __tablename__ = "quiz_results"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
    )

    score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100

    completed_at: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    points_earned: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    # Text answers per question index (for open-ended questions)
    answers: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
