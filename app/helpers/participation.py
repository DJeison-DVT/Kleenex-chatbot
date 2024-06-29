
from httpx import AsyncClient
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.user import User
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

def unpack_user(participation: Participation):
    user = participation['user']
    participation['user'] = User(**user)
    return Participation(**participation)

async def get_participation_by_phone(client: AsyncClient, phone: str):
    endpoint = f"{settings.BASE_URL}{settings.API_STR}{settings.PARTICIPATION_SECTION}/?phone={phone}"
    response = await client.get(endpoint)

    if response.status_code == 404:
        return None
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch participation")
    
    participations = response.json()
    return [unpack_user(participation) for participation in participations]

async def get_participation(client: AsyncClient, **kwargs):
    endpoint = f"{settings.BASE_URL}{settings.API_STR}{settings.PARTICIPATION_SECTION}/"
    response = await client.get(endpoint, params=kwargs)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch participation")
    
    return [unpack_user(participation) for participation in response.json()]

async def get_participation_by_id(client: AsyncClient, id: str):
    endpoint = f"{settings.BASE_URL}{settings.API_STR}{settings.PARTICIPATION_SECTION}/{id}"
    response = await client.get(endpoint)

    if response.status_code == 404:
        return None
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch participation")
    
    return unpack_user(response.json())

async def create_participation(client: AsyncClient, user: User):
    print("creating participation for user", user.phone)
    endpoint = f"{settings.BASE_URL}{settings.API_STR}{settings.PARTICIPATION_SECTION}/"
    response = await client.post(endpoint, json={"user": user.to_dict()})
    if response.status_code != 201:
        raise HTTPException(status_code=500, detail="Failed to create participation")

    return unpack_user(response.json())    

async def update_participation(client, participation: Participation):
    endpoint = f"{settings.BASE_URL}{settings.API_STR}{settings.PARTICIPATION_SECTION}/{participation.id}"
    response = await client.put(endpoint, json=participation.to_dict())
    if response != 200:
        raise HTTPException(status_code=500, detail="Failed to update participation")
    
    return unpack_user(response.json())