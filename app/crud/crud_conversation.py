from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from models.conversation import Conversation
from schemas.conversation import ConversationCreate, ConversationUpdate

async def create_conversation(db: AsyncSession, conversation: ConversationCreate, user_id: UUID) -> Conversation:
    db_conversation = Conversation(
        user_id=user_id,
        message=conversation.message,
        response=conversation.response,
        context=conversation.context,
        topics=conversation.topics,
        parent_id=conversation.parent_id
    )
    db.add(db_conversation)
    await db.commit()
    await db.refresh(db_conversation)
    return db_conversation

async def get_conversation(db: AsyncSession, conversation_id: UUID) -> Optional[Conversation]:
    query = select(Conversation).options(selectinload(Conversation.children)).where(Conversation.id == conversation_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_conversations(db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Conversation]:
    query = select(Conversation).where(Conversation.user_id == user_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_conversations_by_topic(db: AsyncSession, user_id: UUID, topic: str, skip: int = 0, limit: int = 100) -> List[Conversation]:
    query = select(Conversation).where(
        and_(
            Conversation.user_id == user_id,
            Conversation.topics.contains([topic])
        )
    ).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_conversations_by_date_range(db: AsyncSession, user_id: UUID, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100) -> List[Conversation]:
    query = select(Conversation).where(
        and_(
            Conversation.user_id == user_id,
            Conversation.created_at.between(start_date, end_date)
        )
    ).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def update_conversation(db: AsyncSession, conversation_id: UUID, conversation_update: ConversationUpdate) -> Optional[Conversation]:
    db_conversation = await get_conversation(db, conversation_id)
    if db_conversation is None:
        return None
    
    update_data = conversation_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_conversation, field, value)
    
    await db.commit()
    await db.refresh(db_conversation)
    return db_conversation

async def delete_conversation(db: AsyncSession, conversation_id: UUID) -> bool:
    db_conversation = await get_conversation(db, conversation_id)
    if db_conversation is None:
        return False
    
    await db.delete(db_conversation)
    await db.commit()
    return True
