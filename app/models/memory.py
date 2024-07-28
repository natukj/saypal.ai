from datetime import datetime
from sqlalchemy import event, String, DateTime, ForeignKey, Integer, BigInteger, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from typing import Optional

from db.base_class import Base

class Memory(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    discord_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True, index=True)
    conversation_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversation.id"), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    importance: Mapped[int] = mapped_column(Integer, CheckConstraint('importance BETWEEN 1 AND 10'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    #user: Mapped["User"] = relationship("User", back_populates="memories")
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="memories")

    def access(self):
        self.last_accessed_at = datetime.now()

@event.listens_for(Memory, 'load')
def receive_load(target, context):
    target.access()

from models.user import User
from models.conversation import Conversation