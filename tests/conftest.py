"""
WaslAI.jo — Test Configuration
Async test client + isolated in-memory database
"""
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# --- Test Data Fixtures ---
MERCHANT_PAYLOAD = {
    "email": "merchant@test.jo",
    "password": "testpass123",
    "full_name": "Test Merchant",
    "full_name_ar": "تاجر تجريبي",
    "role": "merchant",
    "phone": "+962791234567",
}

INFLUENCER_PAYLOAD = {
    "email": "influencer@test.jo",
    "password": "testpass123",
    "full_name": "Test Influencer",
    "full_name_ar": "مؤثر تجريبي",
    "role": "influencer",
    "phone": "+962797654321",
}
