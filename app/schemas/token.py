from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class RefreshTokenBase(BaseModel):
    token: str
    authenticates_id: Optional[UUID] = None

class RefreshTokenCreate(RefreshTokenBase):
    authenticates_id: UUID

class RefreshTokenUpdate(RefreshTokenBase):
    pass

class RefreshToken(RefreshTokenUpdate):
    model_config = ConfigDict(from_attributes=True)

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[UUID] = None
    refresh: Optional[bool] = False