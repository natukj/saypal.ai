from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional, Union
from uuid import UUID

class PalBase(BaseModel):
    name: str
    personality: Dict[str, Any]
    relationship_status: str = "Just met"
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class PalCreate(PalBase):
    user_identifier: Union[UUID, int]

class PalUpdate(BaseModel):
    name: Optional[str] = None
    personality: Optional[Dict[str, Any]] = None
    relationship_status: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None    

class Pal(PalBase):
    id: UUID
    user_id: UUID
    discord_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True, exclude_unset=True)
