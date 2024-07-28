from datetime import datetime
from sqlalchemy import String, DateTime, ARRAY, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4
from typing import List, Optional

from db.base_class import Base

class User(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False,
    )
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(nullable=True)
    discord_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    birthday: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    occupation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    relationship_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    interests: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    personality_traits: Mapped[dict] = mapped_column(JSONB, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    refresh_tokens: Mapped[list["Token"]] = relationship(
        foreign_keys="[Token.authenticates_id]", back_populates="authenticates", lazy="dynamic"
    )
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="user", cascade="all, delete-orphan", order_by="desc(Conversation.updated_at)", foreign_keys="[Conversation.user_id]")
    active_conversation_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("conversation.id", ondelete="SET NULL"), nullable=True)
    active_conversation: Mapped[Optional["Conversation"]] = relationship("Conversation", foreign_keys=[active_conversation_id], post_update=True)
    pal: Mapped["Pal"] = relationship("Pal", back_populates="user", uselist=False, cascade="all, delete-orphan")


from models.conversation import Conversation
from models.pal import Pal
from models.token import Token