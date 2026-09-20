from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

db_url = settings.DATABASE_URL
if not (db_url.startswith("sqlite+aiosqlite") or db_url.startswith("postgresql+asyncpg")):
    if db_url.startswith("sqlite:"):
        db_url = db_url.replace("sqlite:", "sqlite+aiosqlite:")
    elif db_url.startswith("postgresql:"):
        db_url = db_url.replace("postgresql:", "postgresql+asyncpg:")

engine = create_async_engine(
    db_url,
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
    echo=False
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
