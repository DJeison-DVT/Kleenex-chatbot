import requests
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Tuple
from collections import defaultdict
from typing import Callable
from datetime import datetime

from app.schemas.user import User
from app.schemas.participation import Participation, Status
from app.core.services.users import update_user_by_phone
from app.core.services.participations import update_participation, add_participation
from app.core.services.tickets import upload_to_gcp
from app.chatbot.messages import Message
from app.chatbot.steps import Steps


class ClassMapping:
    def __init__(self, cls: List[Tuple[object, str]]):
        self.map = defaultdict(list)
        for obj, name in cls:
            if obj:
                self.map[obj].append(name)
            else:
                self.map["other"].append(name)

    def get(self, obj):
        return self.map[obj]

    def available(self):
        return self.map.keys()


class Transition(ABC):
    def __init__(self, message_template: str, format_args: Optional[ClassMapping] = None, upload_params: Optional[ClassMapping] = None):
        self.message_template = message_template
        self.format_args = format_args
        self.upload_params = upload_params

    @abstractmethod
    def execute(self, participation: Optional[Participation] = None, message: Optional[Message] = None, response: Optional[str] = None) -> str:
        pass

    def get_template(self) -> str:
        return self.message_template

    async def save_upload_params(self, user: User, participation: Participation, content: str):
        user_phone = user.phone
        print("uploading...")

        for obj, params in self.upload_params.map.items():
            if obj == User and content:
                for param in params:
                    print(
                        f"Saving {obj} with {param} as {content}")
                    setattr(user, param, content)
                    user = await update_user_by_phone(user_phone, user)
                    return user
            elif obj == Participation and content:
                for param in params:
                    # import Participation
                    setattr(participation, param, content)
                    await update_participation(participation.id, participation)
            else:
                for param in params:
                    print(f"Should Save param: {param}")


class WhatsAppTransition(Transition):
    def __init__(self, message_template: str, format_args: Optional[ClassMapping] = None, upload_params: Optional[ClassMapping] = None):
        super().__init__(message_template, format_args, upload_params)


class ResponseDependentTransition(WhatsAppTransition):
    def __init__(self, transitions: Dict[str, str], message_template: str, format_args: Optional[ClassMapping] = None, upload_params: Optional[ClassMapping] = None):
        super().__init__(message_template, format_args, upload_params)
        self.transitions = transitions

    def execute(self, participation: Participation, message: Message):
        user_response = re.sub(r'[^\x00-\x7F]+', '',
                               message.body_content).lower().strip()

        next_step = self.transitions.get(user_response, participation.flow)
        if user_response == "si acepto" or user_response == "confirmar":
            message.body_content = True
        elif user_response == "no acepto":
            message.body_content = False

        if next_step == participation.flow:
            message.body_content = None
        return Steps(next_step)


class ResponseIndependentTransition(WhatsAppTransition):
    def __init__(self, next_step: str, message_template: str, format_args: Optional[ClassMapping] = None, upload_params: Optional[ClassMapping] = None):
        super().__init__(message_template, format_args, upload_params)
        self.next_step = next_step

    def execute(self, participation: Participation = None, message: Message = None):
        return self.next_step


class MultimediaUploadTransition(WhatsAppTransition):
    def __init__(self, success_step: str, failure_step: str, message_template: str, format_args: Optional[ClassMapping] = None, upload_params: Optional[ClassMapping] = None):
        super().__init__(message_template, format_args, upload_params)
        self.success_step = success_step
        self.failure_step = failure_step

    def execute(self, participation: Participation, message: Message):
        if message.num_media > 0:
            try:
                print(message.media_urls)
                media_url = message.media_urls[0]
                r = requests.get(media_url)
                content_type = r.headers['Content-Type']
                # remove the whatsapp: prefix from the number
                if content_type == 'image/jpeg':
                    filename = f'{participation.user.id}/{participation.id}.jpg'
                elif content_type == 'image/png':
                    filename = f'{participation.user.id}/{participation.id}.png'
                else:
                    raise Exception("Invalid file type")

                if not upload_to_gcp(r.content, filename):
                    raise Exception("Failed to upload image")

                message.body_content = filename
                return self.success_step
            except Exception as e:
                print(e)
        return self.failure_step


class DashboardTransition(Transition):
    def __init__(self, message_template: str, transitions: Optional[Dict[str, str]] = None,  format_args: Optional[ClassMapping] = None, upload_params: Optional[ClassMapping] = None, status: Optional[str] = None):
        super().__init__(message_template, format_args, upload_params)
        self.transitions = transitions
        self.status = status

    async def execute(self, participation: Participation, response: str):
        if self.status:
            participation.status = self.status
            await update_participation(participation.id, participation)
        if not self.transitions:
            return
        return self.transitions.get(response, participation.status)


class ServerTransition(Transition):
    def __init__(self, transitions: Dict[bool, str], message_template: str, action: Optional[Callable] = None, format_args: Optional[ClassMapping] = None, upload_params: Optional[ClassMapping] = None, status: Optional[str] = None):
        super().__init__(message_template, format_args, upload_params)
        self.transitions = transitions
        self.action = action
        self.status = status

    async def execute(self, participation: Participation):
        if self.status:
            if self.status == Status.PENDING.value:
                await add_participation(participation)
            participation.status = self.status
            await update_participation(participation.id, participation)
        if not self.transitions:
            return None
        return self.transitions.get(await self.action(participation), participation.flow)
