from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List, Optional

from models.user import User
from schemas.user import UserCreate, UserUpdate

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    db_user = User(
        discord_id=user.discord_id,
        name=user.name,
        birthday=user.birthday,
        occupation=user.occupation,
        relationship_status=user.relationship_status,
        interests=user.interests,
        personality_traits=user.personality_traits
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    query = select(User).options(selectinload(User.pal)).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_user_by_discord_id(db: AsyncSession, discord_id: str) -> Optional[User]:
    query = select(User).options(selectinload(User.pal)).where(User.discord_id == discord_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    query = select(User).options(selectinload(User.pal)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def update_user(db: AsyncSession, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
    db_user = await get_user(db, user_id)
    if db_user is None:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
    db_user = await get_user(db, user_id)
    if db_user is None:
        return False
    
    await db.delete(db_user)
    await db.commit()
    return True