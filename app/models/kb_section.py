from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class KBSection(Base):
    __tablename__ = "kb_sections"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
