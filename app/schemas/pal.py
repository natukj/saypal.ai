from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Dict, Any
from uuid import UUID

class PalBase(BaseModel):
    name: str
    personality: Dict[str, Any]
    relationship_status: str = "Just met"

class PalCreate(PalBase):
    pass

class Pal(PalBase):
    id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True, exclude_unset=True)