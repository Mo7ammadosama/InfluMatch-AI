"""Auth endpoint tests"""
import pytest

TEST_USER = {
    "full_name_en": "Test Merchant",
    "full_name_ar": "تاجر اختبار",
    "email": "test_merchant@waslai.jo",
    "username": "test_merchant",
    "password": "SecurePass123!",
    "role": "merchant"
}

@pytest.mark.asyncio
async def test_register(client):
    resp = await client.post("/api/auth/register", json=TEST_USER)
    assert resp.status_code in (200, 201, 400, 409)  # 409 = already exists in live DB

@pytest.mark.asyncio
async def test_login(client):
    # Register first
    await client.post("/api/auth/register", json=TEST_USER)
    # Login
    resp = await client.post("/api/auth/login", data={
        "username": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_me_endpoint(client):
    await client.post("/api/auth/register", json=TEST_USER)
    login = await client.post("/api/auth/login", data={
        "username": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    token = login.json().get("access_token")
    resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == TEST_USER["email"]
