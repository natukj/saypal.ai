from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, join
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timedelta


from models.conversation import Conversation, Message
from models.user import User
from schemas.conversation import ConversationCreate, ConversationUpdate, MessageCreate

async def create_conversation(db: AsyncSession, conversation: ConversationCreate, discord_id: int) -> Conversation:
    user_query = select(User.id).where(User.discord_id == discord_id)
    user_result = await db.execute(user_query)
    user_id = user_result.scalar_one_or_none()
    
    if not user_id:
        raise ValueError(f"No user found with discord_id: {discord_id}")

    await db.execute(
        update(Conversation)
        .where(and_(Conversation.user_id == user_id, Conversation.is_active == True))
        .values(is_active=False)
    )
    
    db_conversation = Conversation(**conversation.model_dump(), user_id=user_id, is_active=True)
    db.add(db_conversation)
    await db.commit()
    await db.refresh(db_conversation)
    return db_conversation

async def get_conversation(db: AsyncSession, conversation_id: UUID) -> Optional[Conversation]:
    query = select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.id == conversation_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_active_conversation(db: AsyncSession, discord_id: int) -> Optional[Conversation]:
    query = select(Conversation).join(User).where(
        and_(User.discord_id == discord_id, Conversation.is_active == True)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_conversations(db: AsyncSession, discord_id: int, skip: int = 0, limit: int = 100) -> List[Conversation]:
    query = select(Conversation).join(User).where(User.discord_id == discord_id).offset(skip).limit(limit)
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

async def add_message_to_conversation(db: AsyncSession, conversation_id: UUID, message: MessageCreate) -> Message:
    db_message = Message(
        conversation_id=conversation_id,
        content=message.content,
        is_from_user=message.is_from_user
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message

async def get_messages(db: AsyncSession, conversation_id: UUID, skip: int = 0, limit: int = 100) -> List[Message]:
    query = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def update_conversation_last_activity(db: AsyncSession, conversation_id: UUID):
    await db.execute(
        update(Conversation)
        .where(Conversation.id == conversation_id)
        .values(updated_at=datetime.now())
    )
    await db.commit()

async def deactivate_old_conversations(db: AsyncSession, hours: int = 24):
    cutoff_time = datetime.now() - timedelta(hours=hours)
    await db.execute(
        update(Conversation)
        .where(and_(Conversation.is_active == True, Conversation.updated_at < cutoff_time))
        .values(is_active=False)
    )
    await db.commit()

async def get_recent_conversations(db: AsyncSession, discord_id: int, limit: int = 10) -> List[Conversation]:
    query = (
        select(Conversation)
        .join(User)
        .where(User.discord_id == discord_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def get_conversations_by_topics(db: AsyncSession, discord_id: int, topics: List[str], limit: int = 10) -> List[Conversation]:
    query = (
        select(Conversation)
        .join(User)
        .where(and_(
            User.discord_id == discord_id,
            Conversation.topics.overlap(topics)
        ))
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def get_conversations_by_recency_and_topics(
    db: AsyncSession, 
    discord_id: int, 
    topics: Optional[List[str]] = None, 
    days: int = 7, 
    limit: int = 10
) -> List[Conversation]:
    cutoff_date = datetime.now() - timedelta(days=days)
    query = (
        select(Conversation)
        .join(User)
        .where(and_(
            User.discord_id == discord_id,
            Conversation.updated_at >= cutoff_date
        ))
    )
    
    if topics:
        query = query.where(Conversation.topics.overlap(topics))
    
    query = query.order_by(Conversation.updated_at.desc()).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_conversation_analysis_status(db: AsyncSession, conversation_id: UUID, is_analyzed: bool) -> Optional[Conversation]:
    db_conversation = await get_conversation(db, conversation_id)
    if db_conversation is None:
        return None
    
    db_conversation.is_analyzed = is_analyzed
    await db.commit()
    await db.refresh(db_conversation)
    return db_conversation

async def get_unanalyzed_conversations(db: AsyncSession, limit: int = 100) -> List[Conversation]:
    query = select(Conversation).where(Conversation.is_analyzed == False).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
