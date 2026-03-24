from sqlalchemy import Integer, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import AchievementCategory


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str] = mapped_column(String(1000), nullable=False)

    icon: Mapped[str] = mapped_column(String(10), nullable=False)

    category: Mapped[AchievementCategory] = mapped_column(
        SQLEnum(AchievementCategory, name="achievement_category"),
        nullable=False,
    )

    xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
