import urllib.parse
import json
from twilio.rest import Client
from bson import ObjectId
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Tuple, List
from datetime import datetime


from app.schemas.user import User
from app.core.config import settings
from app.core.services.messages import save_message
from app.db.db import MessagesCollection
from app.core.services.datetime_mexico import UTC_to_local

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


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


async def send_message(body: str, user: User, format_args: dict = {}):
    try:
        message = client.messages.create(
            messaging_service_sid=settings.TWILIO_MESSAGING_SERVICE_SID,
            content_sid=body,
            content_variables=json.dumps(format_args) if format_args else None,
            to=user.phone
        )
        await save_message(message.sid, user)
    except Exception as e:
        print(f"Error: {e}")
        raise RuntimeError("Failed to send message")


async def retrieve_body(message_sid: str) -> Tuple[str, str]:
    try:
        message = client.messages(message_sid).fetch()
        body = message.body or None
        url = None
        if int(message.num_media) > 0:
            uris = [media.uri for media in message.media.list()]
            uri = uris[0]
            base_url = "https://api.twilio.com"
            url = f"{base_url}{uri.replace('.json', '')}"

        return body, url

    except Exception as e:
        print(f"Error: {e}")
        raise RuntimeError("Failed to retrieve message")


async def get_user_messages(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid ID")

    cursor = MessagesCollection().find({"client_id": ObjectId(user_id)})
    messages = []
    async for message in cursor:
        message["_id"] = str(message["_id"])
        message["client_id"] = str(message["client_id"])

        text, photo_url = await retrieve_body(message["message_sid"])

        local_datetime = UTC_to_local(message['datetime'])

        messages.append({
            "message_sid": message["message_sid"],
            "from_": message["from"],
            "to": message["to"],
            "datetime": local_datetime,
            "text": text,
            "photo_url": photo_url
        })

    messages.sort(key=lambda x: x["datetime"], reverse=True)

    return messages
