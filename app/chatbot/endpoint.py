import os
import urllib.parse
import requests
from twilio.rest import Client
from httpx import AsyncClient
from fastapi import APIRouter, Request

from app.core.config import settings

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
    client.messages.create(
        from_=message.to_number,
        body=body,
        to=message.from_number,
    )


@router.post("/")
async def webhook(request: Request):
    body_bytes = await request.body()
    message = Message(body_bytes)

    return {"message": "Received", "from": message.from_number}
