import os
import urllib.parse
import requests
from twilio.rest import Client
from httpx import AsyncClient
from fastapi import APIRouter, Request, HTTPException, Response

from app.core.config import settings
from app.chatbot.messages import *
from app.chatbot.flow import FLOW, FlowManager

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

router = APIRouter()


async def get_current_ticket_number(client: AsyncClient):
    try:
        response = await client.get(
            f"{settings.BASE_URL}{settings.API_STR}{settings.PARTICIPATION_SECTION}/count")
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get current ticket number: {str(e)}")

    count = response.json()
    return count['count']


async def get_user(client: AsyncClient, message):
    print("getting user...")
    endpoint = f"{settings.BASE_URL}{settings.API_STR}{settings.USER_SECTION}/{message.from_number}"
    response = await client.get(endpoint)
    if response.status_code == 404:
        return None

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch user")

    user = response.json()
    return user


async def handle_user(client: AsyncClient, user, message):
    print("handling user...")
    flow_manager = FlowManager(FLOW, user)

    flow_manager.execute(client, message)


async def handle_new_user(httpx_client: AsyncClient, message: Message):
    print(f"New user: {message.from_number}")
    response = await httpx_client.post(f"{settings.BASE_URL}{settings.API_STR}{settings.USER_SECTION}/",
                                       json={"phone": message.from_number})

    if response.status_code != 201:
        raise HTTPException(status_code=500, detail="Failed to create user")

    count = await get_current_ticket_number(httpx_client)
    send_message(
        client,
        messages[Steps.ONBOARDING].format(tickets_registered=count),
        message
    )


@ router.post("/")
async def webhook(request: Request, response: Response):
    try:
        body_bytes = await request.body()
        message = Message(body_bytes)
        print(
            f"Received message: {message.body_content}, from: {message.from_number}")
        if not message.body_content or not message.from_number:
            raise AttributeError

        async with AsyncClient() as client:
            user = await get_user(client, message)
            if user:
                await handle_user(client, user, message)
            else:
                await handle_new_user(client, message)
        print("ending...")

        return {"message": "Received", "from": message.from_number}

    except AttributeError:
        error_message = "Invalid message format. Please ensure the message is correctly formatted."
        response.status_code = 400
        return {"error": error_message}

    except HTTPException as http_exc:
        response.status_code = http_exc.status_code
        return {"error": http_exc.detail}

    except Exception as exc:
        response.status_code = 500
        print(f'Exception: {exc}')
        return {"error": "An unexpected error occurred. Please try again later."}
