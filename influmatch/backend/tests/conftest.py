"""Test configuration — async in-memory SQLite"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

class TestBase(DeclarativeBase):
    pass

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    from backend.core.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(test_engine):
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client():
    from backend.main import app
    from backend.core.database import init_db
    await init_db()   # ensure tables exist in test DB
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
