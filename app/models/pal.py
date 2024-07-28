from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4
from typing import Optional

from db.base_class import Base

class Pal(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), unique=True, nullable=False)
    discord_id: Mapped[int] = mapped_column(BigInteger, unique=False, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    personality: Mapped[dict] = mapped_column(JSONB, nullable=False)
    relationship_status: Mapped[str] = mapped_column(String, nullable=False, default="Just met")
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    preferences: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="pal")

from models.user import User