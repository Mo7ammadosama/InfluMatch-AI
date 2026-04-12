"""
InfluMatch.jo — Campaign Tests
create → list → get → update
"""
import pytest
from httpx import AsyncClient
from tests.conftest import MERCHANT_PAYLOAD

CAMPAIGN_PAYLOAD = {
    "title": "Summer Fashion Campaign",
    "title_ar": "حملة الأزياء الصيفية",
    "description": "Looking for fashion influencers in Amman",
    "total_budget_jod": 500.0,
    "target_categories": ["fashion", "lifestyle"],
    "required_platforms": ["instagram", "tiktok"],
    "min_followers": 5000,
    "max_influencers": 3,
    "preferred_languages": ["ar", "en"],
    "target_cities": ["Amman"],
}


async def _get_merchant_token(client: AsyncClient) -> str:
    await client.post("/api/v1/auth/register", json=MERCHANT_PAYLOAD)
    r = await client.post("/api/v1/auth/login", json={
        "email": MERCHANT_PAYLOAD["email"], "password": MERCHANT_PAYLOAD["password"]
    })
    return r.json()["access_token"]


async def _create_merchant_profile(client: AsyncClient, token: str):
    await client.post(
        "/api/v1/merchants/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "business_name": "Test Store", "business_name_ar": "متجر تجريبي",
            "business_category": "fashion", "city": "Amman",
        },
    )


@pytest.mark.asyncio
async def test_create_campaign(client: AsyncClient):
    token = await _get_merchant_token(client)
    await _create_merchant_profile(client, token)
    r = await client.post(
        "/api/v1/campaigns/",
        headers={"Authorization": f"Bearer {token}"},
        json=CAMPAIGN_PAYLOAD,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == CAMPAIGN_PAYLOAD["title"]
    assert data["total_budget_jod"] == CAMPAIGN_PAYLOAD["total_budget_jod"]
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_campaign_budget_minimum(client: AsyncClient):
    token = await _get_merchant_token(client)
    await _create_merchant_profile(client, token)
    r = await client.post(
        "/api/v1/campaigns/",
        headers={"Authorization": f"Bearer {token}"},
        json={**CAMPAIGN_PAYLOAD, "total_budget_jod": 10.0},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_list_campaigns(client: AsyncClient):
    token = await _get_merchant_token(client)
    await _create_merchant_profile(client, token)
    await client.post("/api/v1/campaigns/", headers={"Authorization": f"Bearer {token}"}, json=CAMPAIGN_PAYLOAD)
    r = await client.get("/api/v1/campaigns/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
