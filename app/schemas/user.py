from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from .conversation import Conversation
from .memory import Memory
from .pal import Pal

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    discord_id: Optional[int] = None
    name: str
    birthday: Optional[datetime] = None
    occupation: Optional[str] = None
    relationship_status: Optional[str] = None
    interests: List[str]
    personality_traits: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)

class UserCreateDiscord(UserBase):
    discord_id: int

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    discord_id: Optional[int] = None
    name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=64)
    original_password: str = Field(..., min_length=8, max_length=64)
    birthday: Optional[datetime] = None
    occupation: Optional[str] = None
    relationship_status: Optional[str] = None
    interests: Optional[List[str]] = None
    personality_traits: Optional[Dict[str, Any]] = None
    last_login: Optional[datetime] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)

class UserInDBBase(UserBase):
    id: Optional[UUID] = None
    discord_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class User(UserInDBBase):
    hashed_password: bool = Optional[Field(default=False, alias="password")]
    # not sure about below
    conversations: List[Conversation] = []
    pal: Optional[Pal] = None
    # memories: List[Memory] = []

    @field_validator("hashed_password")
    def evaluate_hashed_password(cls, hashed_password):
        return bool(hashed_password)

    model_config = ConfigDict(from_attributes=True, exclude_unset=True)