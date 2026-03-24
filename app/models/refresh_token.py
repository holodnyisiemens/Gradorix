from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column


from app.core.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

