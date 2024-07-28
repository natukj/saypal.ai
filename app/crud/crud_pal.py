from typing import Optional, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from crud.crud_base import CRUDBase
from models.user import User
from models.pal import Pal
from schemas.pal import PalCreate, PalUpdate

class CRUDPal(CRUDBase[Pal, PalCreate, PalUpdate]):
    async def create_with_user(self, db: AsyncSession, *, obj_in: PalCreate) -> Pal:
        user_id, discord_id = await self.get_user_info(db, obj_in.user_identifier)

        db_obj = Pal(
            user_id=user_id,
            discord_id=discord_id,
            name=obj_in.name,
            personality=obj_in.personality,
            relationship_status=obj_in.relationship_status,
            avatar_url=obj_in.avatar_url,
            bio=obj_in.bio,
            preferences=obj_in.preferences
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

    async def get_by_user_id(self, db: AsyncSession, user_id: UUID) -> Optional[Pal]:
        query = select(Pal).where(Pal.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_discord_id(self, db: AsyncSession, discord_id: int) -> Optional[Pal]:
        query = select(Pal).join(Pal.user).where(Pal.user.discord_id == discord_id)
        result = await db.execute(query)
        return result.scalars().first()

    async def update_pal(self, db: AsyncSession, *, db_obj: Pal, obj_in: PalUpdate) -> Pal:
        update_data = obj_in.dict(exclude_unset=True)
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

pal = CRUDPal(Pal)
