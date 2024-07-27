from datetime import datetime
from sqlalchemy import String, DateTime, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from typing import List, Optional

from db.base_class import Base

class User(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    discord_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    birthday: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    occupation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    relationship_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    interests: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    personality_traits: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False,
    )

    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    pal: Mapped["Pal"] = relationship("Pal", back_populates="user", uselist=False, cascade="all, delete-orphan")

from models.conversation import Conversation
from models.pal import Pal



