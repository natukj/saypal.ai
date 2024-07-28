from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from uuid import UUID
from models.user import User

async def set_active_conversation(db: AsyncSession, user_id: UUID, conversation_id: UUID):
    stmt = update(User).where(User.id == user_id).values(active_conversation_id=conversation_id)
    await db.execute(stmt)
    await db.commit()