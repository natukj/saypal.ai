from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from uuid import UUID

class MessageBase(BaseModel):
    content: str
    is_from_user: bool

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: UUID
    conversation_id: UUID

    model_config = ConfigDict(from_attributes=True)

class ConversationBase(BaseModel):
    dm_channel_id: Optional[int] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    topics: Optional[List[str]] = None
    dm_channel_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_analyzed: Optional[bool] = None

class Conversation(ConversationBase):
    id: UUID
    user_id: UUID
    is_active: bool
    messages: List[Message] = []

    model_config = ConfigDict(from_attributes=True)

