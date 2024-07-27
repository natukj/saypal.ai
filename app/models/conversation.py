from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from typing import List, Optional

from db.base_class import Base

class Conversation(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    response: Mapped[str] = mapped_column(String, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    topics: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    
    parent_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("conversation.id"), nullable=True)
    children: Mapped[List["Conversation"]] = relationship(
        "Conversation",
        backref=relationship("Conversation", remote_side=[id]),
        cascade="all, delete-orphan"
    )

from models.user import User