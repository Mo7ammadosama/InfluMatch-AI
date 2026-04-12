"""Health check tests"""
import pytest

@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_api_docs(client):
    resp = await client.get("/docs")
    assert resp.status_code == 200
