# utils/user_data.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from crud.crud_user import user as user_crud
from crud.crud_memory import memory as memory_crud

async def get_user_discord_data(db: AsyncSession, discord_id: int, recent_conversations_limit: int = 5):
    user_data = await user_crud.get_user_data_by_discord_id(db, discord_id, recent_conversations_limit)
    if not user_data:
        return None

    important_memories = await memory_crud.get_by_importance(db, user_data.id, min_importance=7)

    return {
        "user": user_data,
        "pal": user_data.pal,
        "active_conversation": user_data.active_conversation,
        "recent_conversations": user_data.conversations,
        "important_memories": important_memories
    }
