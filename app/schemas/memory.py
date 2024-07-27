from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID

class MemoryBase(BaseModel):
    content: str
    importance: int = Field(..., ge=1, le=10)

class MemoryCreate(MemoryBase):
    pass

class Memory(MemoryBase):
    id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True, exclude_unset=True)