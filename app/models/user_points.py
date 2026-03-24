from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserPoints(Base):
    __tablename__ = "user_points"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    total_points: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0",
    )

    level: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1",
    )

    level_name: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Новичок",
    )

    points_to_next_level: Mapped[int] = mapped_column(
        Integer, nullable=False, default=100, server_default="100",
    )
