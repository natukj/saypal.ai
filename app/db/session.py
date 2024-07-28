from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import settings

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)