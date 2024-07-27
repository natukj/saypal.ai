from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from db.base_class import Base


class Memory(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    importance: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="memories")

from models.user import User