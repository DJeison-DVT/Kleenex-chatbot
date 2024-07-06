import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.chatbot.steps import Steps

SECTION = "/users/"
FULL_URL = settings.BASE_URL + settings.API_STR + SECTION


@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient() as client:
        response = await client.get(FULL_URL + "1234567890")
        if response.status_code == 200:
            response = await client.delete(FULL_URL + "1234567890")
            assert response.status_code == 204

        response = await client.post(FULL_URL, json={"phone": "1234567890"})

        assert response.status_code == 201
        response = response.json()
        assert response['phone'] == "1234567890"
        assert response['terms'] == False

        response = await client.delete(FULL_URL + "1234567890")
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_create_multiple_users():
    """
    creates multiple users 
    """
    async with AsyncClient() as client:
        response = await client.post(FULL_URL, json={"phone": "1234567890"})
        assert response.status_code == 201
        response = await client.post(FULL_URL, json={"phone": "1234567890"})
        assert response.status_code == 409
        response = await client.post(FULL_URL, json={"phone": "1234567891"})
        assert response.status_code == 201
        response = await client.post(FULL_URL, json={"phone": "1234567892"})
        assert response.status_code == 201


@pytest.mark.asyncio
async def test_fetch_all_users():
    """
    fetches all users
    """
    async with AsyncClient() as client:
        response = await client.get(FULL_URL)
        assert response.status_code == 200
        response = response.json()

        length = len(response)

        response = await client.post(FULL_URL, json={"phone": "1234567899"})
        assert response.status_code == 201

        response = await client.get(FULL_URL)
        assert response.status_code == 200
        response = response.json()
        assert len(response) == length + 1

        response = await client.delete(FULL_URL + "1234567899")


@pytest.mark.asyncio
async def test_fetch_user_by_phone():
    """
    fetches a user by phone number
    """
    async with AsyncClient() as client:
        response = await client.get(FULL_URL + "1234567890")
        assert response.status_code == 200
        response = response.json()
        assert response['phone'] == "1234567890"
        assert response['terms'] == False


@pytest.mark.asyncio
async def test_delete_user_by_phone():
    """
    deletes a user by phone number
    """
    async with AsyncClient() as client:
        response = await client.delete(FULL_URL + "1234567890")
        assert response.status_code == 204
        response = await client.get(FULL_URL + "1234567890")
        assert response.status_code == 404
        response = await client.delete(FULL_URL + "1234567891")
        assert response.status_code == 204
        response = await client.delete(FULL_URL + "1234567892")
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_put_user_registration():
    """
    Simulates a registration flow

    1. Create a user
    2. Update the user with name
    3. Update the user with email
    """
    async with AsyncClient() as client:
        response = await client.post(FULL_URL, json={"phone": "1234567890"})
        assert response.status_code == 201

        user = response.json()
        user['name'] = "Jane Doe"
        user['terms'] = True
        user = {k: v for k, v in user.items() if v is not None}

        response = await client.put(FULL_URL + "1234567890", json=user)
        assert response.status_code == 200
        user = response.json()

        assert user['phone'] == "1234567890"
        assert user['terms'] == True
        assert user['name'] == "Jane Doe"

        user['email'] = "jane.doe@gmail.com"

        response = await client.put(FULL_URL + "1234567890", json=user)
        assert response.status_code == 200
        user = response.json()

        assert user['phone'] == "1234567890"
        assert user['terms'] == True
        assert user['name'] == "Jane Doe"
        assert user['email'] == "jane.doe@gmail.com"

        response = await client.get(FULL_URL + "1234567890")

        assert response.status_code == 200
        user = response.json()
        assert user['phone'] == "1234567890"
        assert user['terms'] == True
        assert user['name'] == "Jane Doe"
        assert user['email'] == "jane.doe@gmail.com"
        assert user['flow_step'] == "onboarding"

        response = await client.delete(FULL_URL + "1234567890")
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_put_user_flow():
    """
    Simulates a flow

    1. Create a user
    2. Update the user
    3. Cycle through all steps
    """
    async with AsyncClient() as client:
        response = await client.post(FULL_URL, json={"phone": "1234567890"})
        assert response.status_code == 201
        user = response.json()
        user['name'] = "Jane Doe"
        user['email'] = "jane.doe@gmail.com"

        response = await client.put(FULL_URL + "1234567890", json=user)
        assert response.status_code == 200
        user = response.json()
        assert user['phone'] == "1234567890"
        assert user['terms'] == False
        assert user['name'] == "Jane Doe"
        assert user['email'] == "jane.doe@gmail.com"

        assert user['flow_step'] == "onboarding"

        test_steps = [step.value for step in Steps]
        test_steps.pop(0)
        for step in test_steps:

            user['flow_step'] = step
            response = await client.put(FULL_URL + "1234567890", json=user)
            assert response.status_code == 200
            user = response.json()
            assert user['phone'] == "1234567890"
            assert user['flow_step'] == step

        response = await client.delete(FULL_URL + "1234567890")
        assert response.status_code == 204
