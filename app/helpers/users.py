from fastapi import HTTPException
from httpx import AsyncClient

from app.schemas.user import User
from app.core.config import settings


async def get_user(client: AsyncClient, phone: str):
    endpoint = f"{settings.BASE_URL}{settings.API_STR}{settings.USER_SECTION}/{phone}"
    response = await client.get(endpoint)
    if response.status_code == 404:
        return None

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch user")

    user = response.json()
    if not user:
        return None
    return User(**user)


async def post_user(client: AsyncClient, phone: str):
    response = await client.post(f"{settings.BASE_URL}{settings.API_STR}{settings.USER_SECTION}/",
                                 json={"phone": phone})
    if response.status_code != 201:
        raise HTTPException(status_code=500, detail="Failed to create user")

    user_dict = response.json()
    if not user_dict:
        return None
    return User(**user_dict)


async def update_user(client: AsyncClient, user: User):
    endpoint = f"{settings.BASE_URL}{settings.API_STR}{settings.USER_SECTION}/{user.phone}"
    response = await client.put(endpoint, json=user.to_dict())
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to update user")
    user_dict = response.json()
    return User(**user_dict)
