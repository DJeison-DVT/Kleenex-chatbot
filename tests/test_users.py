import httpx
import pytest
from httpx import Response
from app.core.config import settings

SECTION = "/users/"
FULL_URL = settings.BASE_URL + settings.API_STR + SECTION

def URLBuilder(path: str) -> str:
    return settings.API_STR + path

async def mock_response(request: httpx.Request) -> Response:
    # Adjusted to match the full URL path
    if request.url.path == URLBuilder(SECTION):
        user_data = {"phone": "1234567890", "terms": True}
        return httpx.Response(status_code=201, json=user_data)
    # Default response for unspecified routes
    return httpx.Response(status_code=404)

@pytest.mark.asyncio
async def test_create_user():
    async with httpx.AsyncClient(transport=httpx.MockTransport(mock_response), base_url=settings.BASE_URL) as client:
        # Now using full URL that matches the mock_response condition
        response = await client.post(URLBuilder(SECTION), json={"name": "Jane Doe"})
        assert response.status_code == 201
        response = response.json()
        print(response)
        assert response == {"phone": "1234567890", "terms": True}

@pytest.mark.asyncio
async def test_create_user_real():
    async with httpx.AsyncClient() as client:
        # already exists 1234567890 delete
        response = await client.get(FULL_URL + "1234567890")
        if response.status_code == 200:
            response = await client.delete(FULL_URL + "1234567890")
            assert response.status_code == 200

        response = await client.post(FULL_URL, json={"phone": "1234567890", "terms": True})
        
        # Assert the expected status code and response body
        assert response.status_code == 200
        response = response.json()
        assert response['phone'] == "1234567890"
        assert response['terms'] == True

        response = await client.delete(FULL_URL + "1234567890")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_multiple_users():
    async with httpx.AsyncClient() as client:
        response = await client.post(FULL_URL, json={"phone": "1234567890", "terms": True})
        assert response.status_code == 200
        response = await client.post(FULL_URL, json={"phone": "1234567890", "terms": True})
        assert response.status_code == 409
        response = await client.post(FULL_URL, json={"phone": "1234567891", "terms": True})
        assert response.status_code == 200
        response = await client.post(FULL_URL, json={"phone": "1234567892", "terms": True})
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_fetch_all_users():
    async with httpx.AsyncClient() as client:
        response = await client.get(FULL_URL)
        assert response.status_code == 200
        response = response.json()
        assert len(response) == 3
    
@pytest.mark.asyncio
async def test_fetch_user_by_phone():
    async with httpx.AsyncClient() as client:
        response = await client.get(FULL_URL + "1234567890")
        assert response.status_code == 200
        response = response.json()
        assert response['phone'] == "1234567890"
        assert response['terms'] == True

@pytest.mark.asyncio
async def test_delete_user_by_phone():
    async with httpx.AsyncClient() as client:
        response = await client.delete(FULL_URL + "1234567890")
        assert response.status_code == 200
        response = await client.get(FULL_URL + "1234567890")
        assert response.status_code == 404
        response = await client.delete(FULL_URL + "1234567891")
        assert response.status_code == 200
        response = await client.delete(FULL_URL + "1234567892")
        assert response.status_code == 200
