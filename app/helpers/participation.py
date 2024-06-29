
from httpx import AsyncClient
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.participation import Participation

async def get_current_ticket_number(client: AsyncClient):
    endpoint = f"{settings.BASE_URL}{settings.API_STR}{settings.PARTICIPATION_SECTION}/count"
    try:
        response = await client.get(endpoint)
    except Exception as e:
        print(f"Failed to get current ticket number: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get current ticket number: {str(e)}")

    count = response.json()
    return count['count']

async def get_participation_by_phone(client: AsyncClient, phone: str):
    endpoint = f"{settings.BASE_URL}{settings.API_STR}{settings.PARTICIPATION_SECTION}/phone/{phone}"
    response = await client.get(endpoint)

    if response.status_code == 404:
        return None
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch participation")
    
    user = response.json()
    return user

async def update_participation(client, participation: Participation):
    endpoint = f"{settings.BASE_URL}{settings.API_STR}{settings.PARTICIPATION_SECTION}/{participation.id}"
    response = await client.put(endpoint, json=participation.to_dict())
    if response != 200:
        raise HTTPException(status_code=500, detail="Failed to update participation")