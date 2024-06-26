import os
import urllib.parse
import requests
from twilio.rest import Client
from httpx import AsyncClient
from fastapi import APIRouter, Request, HTTPException, Response

from app.core.config import settings
from app.chatbot.messages import *
from app.chatbot.flow import FLOW, FlowManager
from app.helpers.users import get_current_ticket_number, get_user

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

router = APIRouter()


async def handle_user(httpx_client: AsyncClient, user, message):
    print("handling user...")
    flow_manager = FlowManager(FLOW, user)

    await flow_manager.execute(client, httpx_client, message)


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
            user = await get_user(client, message.from_number)
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