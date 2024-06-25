import os
import urllib.parse
import requests
from twilio.rest import Client
from httpx import AsyncClient
from fastapi import APIRouter, Request, HTTPException

from app.core.config import settings
from app.chatbot.messages_offline import messages

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

router = APIRouter()


class Message:
    def __init__(self, body):
        body_str = body.decode()
        parsed_body = urllib.parse.parse_qs(body_str)

        # Unique ID of the message
        self.sms_message_sid = parsed_body.get('SmsMessageSid', [None])[0]
        # Number of media files in the message
        self.num_media = int(parsed_body.get(
            'NumMedia', [0])[0])  # Convert to int
        # WhatsApp Profile name
        self.profile_name = parsed_body.get('ProfileName', [None])[0]
        # Type of message (e.g. 'text', 'image', 'audio', etc.)
        self.message_type = parsed_body.get('MessageType', [None])[0]
        # Content of the message
        self.body_content = parsed_body.get('Body', [None])[0]
        self.from_number = parsed_body.get('From', [None])[0]
        self.to_number = parsed_body.get('To', [None])[0]
        # Store media URLs if any
        self.media_urls = []
        if self.num_media > 0:
            self.media_urls = [
                urllib.parse.unquote(
                    parsed_body.get(f'MediaUrl{i}', [None])[0])
                for i in range(self.num_media)
            ]

    def download_media(self, folder_path='downloaded_media'):
        # Local Download Placeholder
        # TODO Implement download to cloud storage
        # Ensure the folder exists
        os.makedirs(folder_path, exist_ok=True)

        # Download each media file
        for url in self.media_urls:
            if url:
                response = requests.get(url)
                if response.status_code == 200:
                    file_path = os.path.join(
                        folder_path, f"media_{self.sms_message_sid}_{self.media_urls.index(url)}.jpeg")
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    print(f"Downloaded {file_path}")
                else:
                    print(f"Failed to download media from {url}")


def send_message(message: Message, body: str):
    try:
        client.messages.create(
            from_=message.to_number,
            body=body,
            to=message.from_number,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


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

    match user.flow:
        case "onboarding":
            pass
        case _:
            pass


async def handle_new_user(client: AsyncClient, message):
    print(f"New user: {message.from_number}")
    response = await client.post(f"{settings.BASE_URL}{settings.API_STR}{settings.USER_SECTION}/",
                                 json={"phone": message.from_number})

    if response.status_code != 201:
        raise HTTPException(status_code=500, detail="Failed to create user")

    count = await get_current_ticket_number(client)
    send_message(message, messages["welcome"].format(tickets_registered=count))


@ router.post("/")
async def webhook(request: Request):
    message = None
    try:
        body_bytes = await request.body()
        message = Message(body_bytes)

        print(
            f"Received message: {message.body_content}, from: {message.from_number}")

        async with AsyncClient() as client:
            user = await get_user(client, message)
            if user:
                await handle_user(client, user, message)
            else:
                await handle_new_user(client, message)

        return {"message": "Received", "from": message.from_number}
    except HTTPException as http_exc:
        send_message(message, messages["error"])
        return {"error code": http_exc.status_code, "error": http_exc.detail}
    except Exception as exc:
        return {"error": f"An unexpected error occurred: {str(exc)}"}
