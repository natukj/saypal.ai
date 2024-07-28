from pydantic import BaseModel, ConfigDict, HttpUrl
from typing import List, Optional, Union
from uuid import UUID
import enum

class MediaType(enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    GIF = "gif"
    MEME = "meme"
    LINK = "link"

class MediaBase(BaseModel):
    url: HttpUrl
    type: MediaType
    title: Optional[str] = None
    description: Optional[str] = None

class MediaCreate(MediaBase):
    pass

class Media(MediaBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)

class MessageBase(BaseModel):
    content: str
    is_from_user: bool
    media_id: Optional[UUID] = None

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: UUID
    conversation_id: UUID
    media: Optional[Media] = None

    model_config = ConfigDict(from_attributes=True)

class ConversationBase(BaseModel):
    dm_channel_id: Optional[int] = None
    title: Optional[str] = None
    topics: Optional[List[str]] = None

class ConversationCreate(ConversationBase):
    user_identifier: Union[UUID, int]

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    topics: Optional[List[str]] = None
    dm_channel_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_analyzed: Optional[bool] = None

class Conversation(ConversationBase):
    id: UUID
    user_id: UUID
    discord_id: Optional[int] = None
    is_active: bool
    messages: List[Message] = []

    model_config = ConfigDict(from_attributes=True)

