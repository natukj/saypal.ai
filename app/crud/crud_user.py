from typing import Any, Dict, Optional, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.security import get_password_hash, verify_password
from crud.crud_base import CRUDBase
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserCreateDiscord

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_discord_id(self, db: AsyncSession, *, discord_id: int) -> Optional[User]:
        query = select(User).where(User.discord_id == discord_id)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_user_data_by_discord_id(self, db: AsyncSession, discord_id: int, recent_conversations_limit: int = 5):
        query = (
            select(User)
            .options(
                selectinload(User.pal),
                selectinload(User.active_conversation),
                selectinload(User.conversations.limit(recent_conversations_limit))
            )
            .where(User.discord_id == discord_id)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def set_active_conversation(self, db: AsyncSession, user_id: UUID, conversation_id: UUID):
        user = await self.get(db, id=user_id)
        if user:
            user.active_conversation_id = conversation_id
            await db.commit()
            await db.refresh(user)
        return user

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            name=obj_in.name,
            birthday=obj_in.birthday,
            occupation=obj_in.occupation,
            relationship_status=obj_in.relationship_status,
            interests=obj_in.interests,
            personality_traits=obj_in.personality_traits,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create_with_discord(self, db: AsyncSession, *, obj_in: UserCreateDiscord) -> User:
        db_obj = User(
            discord_id=obj_in.discord_id,
            name=obj_in.name,
            email=obj_in.email,  # could be None
            birthday=obj_in.birthday,
            occupation=obj_in.occupation,
            relationship_status=obj_in.relationship_status,
            interests=obj_in.interests,
            personality_traits=obj_in.personality_traits,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> Optional[User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def authenticate_discord(self, db: AsyncSession, *, discord_id: int) -> Optional[User]:
        return await self.get_by_discord_id(db, discord_id=discord_id)

    async def link_discord_account(self, db: AsyncSession, *, user_id: UUID, discord_id: int) -> User:
        user = await self.get(db, id=user_id)
        if user:
            user.discord_id = discord_id
            await db.commit()
            await db.refresh(user)
        return user

user = CRUDUser(User)
