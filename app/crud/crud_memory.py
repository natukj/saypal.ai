from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List, Optional

from models.memory import Memory
from schemas.memory import MemoryCreate, MemoryUpdate

async def create_memory(db: AsyncSession, memory: MemoryCreate, user_id: UUID) -> Memory:
    db_memory = Memory(
        user_id=user_id,
        content=memory.content,
        importance=memory.importance
    )
    db.add(db_memory)
    await db.commit()
    await db.refresh(db_memory)
    return db_memory

async def get_memory(db: AsyncSession, memory_id: UUID) -> Optional[Memory]:
    query = select(Memory).where(Memory.id == memory_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_memories(db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Memory]:
    query = select(Memory).where(Memory.user_id == user_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_important_memories(db: AsyncSession, user_id: UUID, importance_threshold: int, limit: int = 10) -> List[Memory]:
    query = select(Memory).where(
        Memory.user_id == user_id,
        Memory.importance >= importance_threshold
    ).order_by(Memory.importance.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def update_memory(db: AsyncSession, memory_id: UUID, memory_update: MemoryUpdate) -> Optional[Memory]:
    db_memory = await get_memory(db, memory_id)
    if db_memory is None:
        return None
    
    update_data = memory_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_memory, field, value)
    
    await db.commit()
    await db.refresh(db_memory)
    return db_memory

async def delete_memory(db: AsyncSession, memory_id: UUID) -> bool:
    db_memory = await get_memory(db, memory_id)
    if db_memory is None:
        return False
    
    await db.delete(db_memory)
    await db.commit()
    return True
