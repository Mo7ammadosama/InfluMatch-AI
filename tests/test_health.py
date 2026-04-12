"""
InfluMatch.jo — Health Check & Root Tests
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert data["currency"] == "JOD"
    assert data["market"] == "Jordan"


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    r = await client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "docs" in data


@pytest.mark.asyncio
async def test_docs_available(client: AsyncClient):
    r = await client.get("/docs")
    assert r.status_code == 200
