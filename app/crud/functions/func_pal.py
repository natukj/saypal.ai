from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional

from models.user import Pal

async def create_pal(db: AsyncSession, user_id: UUID, pal_data: dict) -> Pal:
    db_pal = Pal(user_id=user_id, **pal_data)
    db.add(db_pal)
    await db.commit()
    await db.refresh(db_pal)
    return db_pal

async def get_pal(db: AsyncSession, user_id: UUID) -> Optional[Pal]:
    query = select(Pal).where(Pal.user_id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_pal(db: AsyncSession, user_id: UUID, pal_update: dict) -> Optional[Pal]:
    db_pal = await get_pal(db, user_id)
    if db_pal is None:
        return None
    
    for field, value in pal_update.items():
        setattr(db_pal, field, value)
    
    await db.commit()
    await db.refresh(db_pal)
    return db_pal

async def delete_pal(db: AsyncSession, user_id: UUID) -> bool:
    db_pal = await get_pal(db, user_id)
    if db_pal is None:
        return False
    
    await db.delete(db_pal)
    await db.commit()
    return True