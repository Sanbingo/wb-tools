from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
from passlib.hash import bcrypt
from .config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        from .models import Sale, Order, Stock, DailySummary, SyncLog, User  # noqa
        await conn.run_sync(Base.metadata.create_all)

    # Seed default user
    async with async_session() as session:
        from .models import User
        existing = await session.execute(select(User).where(User.username == "WB"))
        if not existing.scalar_one_or_none():
            session.add(User(username="WB", password_hash=bcrypt.hash("000111")))
            await session.commit()
