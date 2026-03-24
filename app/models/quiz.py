from sqlalchemy import Boolean, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str] = mapped_column(String(1000), nullable=False)

    category: Mapped[str] = mapped_column(String(100), nullable=False)

    duration_min: Mapped[int] = mapped_column(Integer, nullable=False, default=10, server_default="10")

    # list of {id, text, type, options?, correctAnswers?}
    questions: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    available: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true",
    )
