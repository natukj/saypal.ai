from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from .conversation import Conversation
from .memory import Memory
from .pal import Pal

class UserBase(BaseModel):
    discord_id: str
    name: str
    birthday: Optional[datetime] = None
    occupation: Optional[str] = None
    relationship_status: Optional[str] = None
    interests: List[str]
    personality_traits: Dict[str, Any]

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    birthday: Optional[datetime] = None
    occupation: Optional[str] = None
    relationship_status: Optional[str] = None
    interests: Optional[List[str]] = None
    personality_traits: Optional[Dict[str, Any]] = None

class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    conversations: List[Conversation] = []
    pal: Optional[Pal] = None
    memories: List[Memory] = []

    model_config = ConfigDict(from_attributes=True, exclude_unset=True)
