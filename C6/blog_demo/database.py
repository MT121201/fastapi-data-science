from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from C6.blog_demo.models import Base

DATABASE_URL = "sqlite+aiosqlite:///chapter06_sqlalchemy.db"
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)


#open a fresh session when the
# request starts and close it when we answered the request
async def get_async_session() -> AsyncIterator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)