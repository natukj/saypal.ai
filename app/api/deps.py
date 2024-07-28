from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

import crud, models, schemas
from core.config import settings
from db.session import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/oauth",
    auto_error=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_token_payload(token: str ) -> schemas.TokenPayload:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO]
        )
        token_payload = schemas.TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return token_payload

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> models.User:
    token_payload = await get_token_payload(token)
    user = await crud.user.get(db, id=token_payload.sub)
    if token_payload.refresh: # or not token_payload.totp:
        # refresh token is not a valid access token and 
        # TOTP False cannot be used to validate TOTP
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="TOTP verification required",
        )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_refresh_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> models.User:
    async with db.begin():
        token_payload = await get_token_payload(token)
        if not token_payload.refresh:
            # access token is not a valid refresh token
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh token required",
            )
        user = await crud.user.get(db, id=token_payload.sub)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not crud.user.is_active(user):
            raise HTTPException(status_code=400, detail="Inactive user")
        # check and revoke this refresh token
        token_obj = await crud.token.get(token=token, user=user)
        if not token_obj:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        await crud.token.remove(db, db_obj=token_obj)
    return user