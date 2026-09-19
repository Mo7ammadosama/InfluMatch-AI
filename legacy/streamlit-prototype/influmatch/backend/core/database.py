"""
WaslAI.jo — Database Engine
Module 02 | SQLAlchemy 2.0 async — SQLite dev / PostgreSQL prod-ready
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from loguru import logger
from .config import get_settings

settings = get_settings()

# Convert sync sqlite URL → async (idempotent)
_db_url = settings.database_url
if "sqlite" in _db_url and "+aiosqlite" not in _db_url:
    _db_url = _db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
if "postgresql" in _db_url and "+asyncpg" not in _db_url:
    _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://")
ASYNC_DATABASE_URL = _db_url

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.debug,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in ASYNC_DATABASE_URL else {},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    # create_all kept for local dev convenience.
    # In production, run: alembic upgrade head
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.success("[ARIA::DB] Tables ready")
