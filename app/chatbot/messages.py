import os
import urllib.parse
import json
import requests
from twilio.rest import Client

from app.schemas.user import User
from app.core.config import settings

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
                else:
                    print(f"Failed to download media from {url}")


def send_message(body: str, user: User, format_args: dict = {}):
    try:
        client.messages.create(
            messaging_service_sid=settings.TWILIO_MESSAGING_SERVICE_SID,
            content_sid=body,
            content_variables=json.dumps(format_args) if format_args else None,
            to=user.phone
        )
    except Exception as e:
        print(f"Error: {e}")
        raise RuntimeError("Failed to send message")
