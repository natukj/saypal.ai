from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from sqlalchemy.orm import selectinload

from crud.crud_base import CRUDBase
from models.user import User
from models.conversation import Conversation, Message
from schemas.conversation import ConversationCreate, ConversationUpdate, MessageCreate
from db.operations import set_active_conversation

class CRUDConversation(CRUDBase[Conversation, ConversationCreate, ConversationUpdate]):
    async def create_with_messages(self, db: AsyncSession, *, obj_in: ConversationCreate) -> Conversation:
        user_id, discord_id = await self.get_user_info(db, obj_in.user_identifier)

        await db.execute(
            update(Conversation)
            .where(and_(Conversation.user_id == user_id, Conversation.is_active == True))
            .values(is_active=False)
        )
        
        db_obj = Conversation(
            user_id=user_id,
            discord_id=discord_id,
            dm_channel_id=obj_in.dm_channel_id,
            title=obj_in.title,
            topics=obj_in.topics,
            is_active=True,
            is_analyzed=False
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # set active conversation
        await set_active_conversation(db, user_id, db_obj.id)
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

    async def get_with_messages(self, db: AsyncSession, id: UUID) -> Optional[Conversation]:
        query = select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_active_by_user(self, db: AsyncSession, user_id: UUID) -> List[Conversation]:
        query = select(Conversation).where(and_(Conversation.user_id == user_id, Conversation.is_active == True))
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_discord_id(self, db: AsyncSession, discord_id: int) -> List[Conversation]:
        query = select(Conversation).where(Conversation.discord_id == discord_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def add_message(self, db: AsyncSession, *, conversation_id: UUID, message: MessageCreate) -> Message:
        db_message = Message(
            conversation_id=conversation_id,
            content=message.content,
            is_from_user=message.is_from_user
        )
        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
        return db_message

    async def get_messages(self, db: AsyncSession, *, conversation_id: UUID, skip: int = 0, limit: int = 100) -> List[Message]:
        query = select(Message).where(Message.conversation_id == conversation_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def update_conversation(self, db: AsyncSession, *, db_obj: Conversation, obj_in: ConversationUpdate) -> Conversation:
        update_data = obj_in.model_dump(exclude_unset=True)
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def set_analyzed(self, db: AsyncSession, *, conversation_id: UUID, is_analyzed: bool) -> Conversation:
        conversation = await self.get(db, id=conversation_id)
        if conversation:
            conversation.is_analyzed = is_analyzed
            await db.commit()
            await db.refresh(conversation)
        return conversation

    async def set_active(self, db: AsyncSession, *, conversation_id: UUID, is_active: bool) -> Conversation:
        conversation = await self.get(db, id=conversation_id)
        if conversation:
            conversation.is_active = is_active
            await db.commit()
            await db.refresh(conversation)
        return conversation

conversation = CRUDConversation(Conversation)
