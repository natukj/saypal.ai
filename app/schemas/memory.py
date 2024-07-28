from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import Union, Optional

class MemoryBase(BaseModel):
    content: str
    importance: int = Field(..., ge=1, le=10)
    conversation_id: UUID

class MemoryCreate(MemoryBase):
    user_identifier: Union[UUID, int]

class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    importance: Optional[int] = Field(None, ge=1, le=10)
    conversation_id: Optional[UUID] = None

class Memory(MemoryBase):
    id: UUID
    user_id: UUID
    discord_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True, exclude_unset=True)
