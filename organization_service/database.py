from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from models import Base

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./organisation_service.db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
