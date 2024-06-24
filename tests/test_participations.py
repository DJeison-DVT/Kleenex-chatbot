import pytest
from httpx import AsyncClient
from datetime import datetime

from app.core.config import settings
from .test_users import SECTION as USER_SECTION

SECTION = "/participations/"
PHONE = "1234567890"
API_URL = settings.BASE_URL + settings.API_STR
FULL_URL = API_URL + SECTION


@pytest.mark.asyncio
async def test_create_participation():
    async with AsyncClient() as client:
        response = await client.post(API_URL + USER_SECTION, json={"phone": PHONE, "terms": True})
        assert response.status_code == 201

        user = response.json()

        response = await client.post(FULL_URL, json={"user": user})
        assert response.status_code == 201

        participation = response.json()

        response = await client.delete(FULL_URL + participation["_id"])
        assert response.status_code == 204

        await client.delete(API_URL + USER_SECTION + PHONE)


@pytest.mark.asyncio
async def test_fetch_participation_by_id():
    async with AsyncClient() as client:
        response = await client.post(API_URL + USER_SECTION, json={"phone": PHONE, "terms": True})
        assert response.status_code == 201

        user = response.json()

        response = await client.post(FULL_URL, json={"user": user})
        assert response.status_code == 201

        participation = response.json()

        response = await client.get(FULL_URL + participation["_id"])
        assert response.status_code == 200

        response = await client.delete(FULL_URL + participation["_id"])
        assert response.status_code == 204

        await client.delete(API_URL + USER_SECTION + PHONE)
