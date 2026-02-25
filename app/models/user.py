from typing import Optional

from sqlalchemy import Boolean, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.schemas.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, name="user_role"), nullable=False)

    firstname: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    lastname: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true",
    )

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"
