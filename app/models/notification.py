from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(String(1000), nullable=False)

    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false",
    )
