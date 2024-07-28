import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from crud.crud_user import user as crud_user
from crud.crud_conversation import conversation as crud_conversation
from crud.crud_pal import pal as crud_pal
from crud.crud_memory import memory as crud_memory
from schemas.user import UserCreate, UserUpdate
from schemas.conversation import ConversationCreate, MessageCreate
from schemas.pal import PalCreate
from schemas.memory import MemoryCreate
from models.user import User
from models.conversation import Conversation

# Create async engine and session
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_test_users(db: AsyncSession):
    user_data = [
        UserCreate(
            email="user333@example.com",
            password="password123",
            name="User One",
            birthday=datetime.now() - timedelta(days=365*25),
            occupation="Software Developer",
            relationship_status="Single",
            interests=["coding", "hiking"],
            personality_traits={"openness": 0.8, "conscientiousness": 0.7}
        ),
        UserCreate(
            email="user343@example.com",
            password="password123",
            name="User Two",
            birthday=datetime.now() - timedelta(days=365*30),
            occupation="Teacher",
            relationship_status="Married",
            interests=["reading", "traveling"],
            personality_traits={"extraversion": 0.6, "agreeableness": 0.9}
        )
    ]
    
    created_users = []
    for i, user in enumerate(user_data):
        db_user = await crud_user.create(db, obj_in=user)
        discord_id = 10000003022 + i  
        user_update = UserUpdate(discord_id=discord_id, original_password=user.password)
        db_user = await crud_user.update(db, db_obj=db_user, obj_in=user_update)
        created_users.append(db_user)
    
    return [user.id for user in created_users]

async def create_test_conversations(db: AsyncSession, users):
    for user in users:
        conv_create = ConversationCreate(
            user_identifier=user.discord_id,  # or user.id if you prefer to use UUID
            dm_channel_id=9876543213,  
            title="Test Conversation",
            topics=["AI", "Machine Learning"]
        )
        db_conv = await crud_conversation.create_with_messages(db, obj_in=conv_create)
        
        # Add some messages to the conversation
        messages = [
            MessageCreate(content="Hello, AI!", is_from_user=True),
            MessageCreate(content="Hello! How can I assist you today?", is_from_user=False),
            MessageCreate(content="Tell me about machine learning.", is_from_user=True),
            MessageCreate(content="Machine learning is a subset of artificial intelligence...", is_from_user=False)
        ]
        for msg in messages:
            await crud_conversation.add_message(db, conversation_id=db_conv.id, message=msg)

async def create_test_pals(db: AsyncSession, users):
    for user in users:
        pal_create = PalCreate(
            user_identifier=user.discord_id,
            name=f"{user.name}'s Pal",
            personality={"friendly": 0.9, "knowledgeable": 0.8},
            relationship_status="Best Friends",
            avatar_url="https://example.com/avatar.jpg",
            bio="I'm an AI companion!",
            preferences={"favorite_topic": "science"}
        )
        await crud_pal.create_with_user(db, obj_in=pal_create)

async def fetch_users_and_conversations(db: AsyncSession):
    stmt = select(User).options(selectinload(User.conversations))
    result = await db.execute(stmt)
    return result.scalars().all()

async def fetch_all_conversations(db: AsyncSession):
    stmt = select(Conversation)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_test_memories(db: AsyncSession, users, conversations):
    for user in users:
        # Use the first conversation from the list of all conversations
        if conversations:
            conversation = conversations[0]
            memories = [
                MemoryCreate(
                    user_identifier=user.discord_id,
                    conversation_id=conversation.id,
                    content="User likes hiking and coding",
                    importance=8
                ),
                MemoryCreate(
                    user_identifier=user.discord_id,
                    conversation_id=conversation.id,
                    content="User is interested in machine learning",
                    importance=7
                )
            ]
            for memory in memories:
                created_memory = await crud_memory.create_with_user(db, obj_in=memory)
                print(f"Created memory for user {user.id} in conversation {conversation.id}")
        else:
            print("No conversations found, skipping memory creation.")

async def main_1():
    async with AsyncSessionLocal() as session:
        user_ids = await create_test_users(session)
        
        # Fetch users with their conversations
        stmt = select(User).where(User.id.in_(user_ids)).options(selectinload(User.conversations))
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        await create_test_conversations(session, users)
        await create_test_pals(session, users)

async def main_2():
    async with AsyncSessionLocal() as session:
        users = await fetch_users_and_conversations(session)
        conversations = await fetch_all_conversations(session)
        
        print(f"Fetched {len(users)} users and {len(conversations)} conversations")
        
        for user in users:
            print(f"User ID: {user.id}, Discord ID: {user.discord_id}")
            print(f"User's conversations: {[conv.id for conv in user.conversations]}")
        
        await create_test_memories(session, users, conversations)

if __name__ == "__main__":
    asyncio.run(main_1())
    asyncio.run(main_2())
