import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from core.config import settings
from db.base import Base

async def drop_all_tables_cascade(engine):
    async with engine.connect() as conn:
        # Fetch all table names
        result = await conn.execute(text("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
        """))
        tables = [row[0] for row in result.fetchall()]
        
        # Drop each table with CASCADE to remove any dependent constraints
        for table in tables:
            await conn.execute(text(f"DROP TABLE IF EXISTS \"{table}\" CASCADE;"))
        await conn.commit()


async def init_db():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True)
    
    async with engine.begin() as conn:
        await drop_all_tables_cascade(engine)
        #await conn.run_sync(Base.metadata.drop_all) # CARE DROP ALL TABLES
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()

    print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())