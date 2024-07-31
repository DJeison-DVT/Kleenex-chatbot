import os
import urllib.parse
import json
import requests
from twilio.rest import Client

from app.schemas.user import User
from app.core.config import settings
from app.core.services.messages import save_message

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


async def retrieve_body(message_sid: str):
    try:
        message = client.messages(message_sid).fetch()
    except Exception as e:
        print(f"Error: {e}")
        raise RuntimeError("Failed to retrieve message")
    return message
