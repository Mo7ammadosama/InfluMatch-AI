"""
WaslAI.jo — Auth Tests
register → login → token → /me
"""
import pytest
from httpx import AsyncClient
from tests.conftest import MERCHANT_PAYLOAD, INFLUENCER_PAYLOAD


@pytest.mark.asyncio
async def test_register_merchant(client: AsyncClient):
    r = await client.post("/api/v1/auth/register", json=MERCHANT_PAYLOAD)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == MERCHANT_PAYLOAD["email"]
    assert data["role"] == "merchant"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=MERCHANT_PAYLOAD)
    r = await client.post("/api/v1/auth/register", json=MERCHANT_PAYLOAD)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=MERCHANT_PAYLOAD)
    r = await client.post("/api/v1/auth/login", json={
        "email": MERCHANT_PAYLOAD["email"],
        "password": MERCHANT_PAYLOAD["password"],
    })
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=MERCHANT_PAYLOAD)
    r = await client.post("/api/v1/auth/login", json={
        "email": MERCHANT_PAYLOAD["email"],
        "password": "wrongpassword",
    })
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=MERCHANT_PAYLOAD)
    login_r = await client.post("/api/v1/auth/login", json={
        "email": MERCHANT_PAYLOAD["email"],
        "password": MERCHANT_PAYLOAD["password"],
    })
    token = login_r.json()["access_token"]
    r = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == MERCHANT_PAYLOAD["email"]


@pytest.mark.asyncio
async def test_register_influencer(client: AsyncClient):
    r = await client.post("/api/v1/auth/register", json=INFLUENCER_PAYLOAD)
    assert r.status_code == 201
    assert r.json()["role"] == "influencer"
