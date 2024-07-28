from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from crud.crud_base import CRUDBase
from models.user import User
from models.memory import Memory
from schemas.memory import MemoryCreate, MemoryUpdate

class CRUDMemory(CRUDBase[Memory, MemoryCreate, MemoryUpdate]):
    async def create_with_user(self, db: AsyncSession, *, obj_in: MemoryCreate) -> Memory:
        user_id, discord_id = await self.get_user_info(db, obj_in.user_identifier)
        db_obj = Memory(
            user_id=user_id,
            discord_id=discord_id,
            conversation_id=obj_in.conversation_id,
            content=obj_in.content,
            importance=obj_in.importance
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_user_info(self, db: AsyncSession, user_identifier: Union[UUID, int]) -> tuple[UUID, Optional[int]]:
        if isinstance(user_identifier, UUID):
            stmt = select(User.id, User.discord_id).where(User.id == user_identifier)
        else:
            stmt = select(User.id, User.discord_id).where(User.discord_id == user_identifier)
        
        result = await db.execute(stmt)
        user_info = result.first()
        
        if user_info is None:
            raise ValueError(f"No user found with identifier {user_identifier}")
        
        return user_info.id, user_info.discord_id

    async def get_by_user(self, db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Memory]:
        query = select(Memory).where(Memory.user_id == user_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_conversation(self, db: AsyncSession, conversation_id: UUID) -> List[Memory]:
        query = select(Memory).where(Memory.conversation_id == conversation_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_importance(self, db: AsyncSession, user_id: UUID, min_importance: int) -> List[Memory]:
        query = select(Memory).where(and_(Memory.user_id == user_id, Memory.importance >= min_importance))
        result = await db.execute(query)
        return result.scalars().all()

    async def update_memory(self, db: AsyncSession, *, db_obj: Memory, obj_in: MemoryUpdate) -> Memory:
        update_data = obj_in.model_dump(exclude_unset=True)
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def access_memory(self, db: AsyncSession, memory_id: UUID) -> Optional[Memory]:
        memory = await self.get(db, id=memory_id)
        if memory:
            memory.last_accessed_at = datetime.utcnow()
            await db.commit()
            await db.refresh(memory)
        return memory

memory = CRUDMemory(Memory)
