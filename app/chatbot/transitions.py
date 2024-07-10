
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Tuple
from collections import defaultdict
from typing import Callable

from app.schemas.user import User
from app.schemas.participation import Participation
from app.core.services.users import fetch_user_by_phone, update_user_by_phone
from app.core.services.participations import fetch_participation_by_phone, update_participation
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

    async def save_upload_params(self, message: Optional[Message] = None, response: Optional[str] = None):
        user_phone = message.from_number if message else response.from_number
        print("uploading...")

        for obj, params in self.upload_params.map.items():
            if obj == User and message.body_content:
                for param in params:
                    print(
                        f"Saving {obj} with {param} as {message.body_content}")
                    user = await fetch_user_by_phone(user_phone)
                    print(user)
                    print("changing:", param, "to:", message.body_content)
                    setattr(user, param, message.body_content)
                    user = await update_user_by_phone(user_phone, user)
                    return user
            elif obj == Participation and message.body_content:
                for param in params:
                    participation = await fetch_participation_by_phone(user_phone)
                    setattr(participation, param, message.body_content)
                    await update_participation(participation)
            else:
                for param in params:
                    print(f"Save param: {param}")


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

    # TODO upload to bucket
    def execute(self, participation: Participation = None, message: Message = None):
        if message and message.num_media > 0:
            return self.success_step
        return self.failure_step


class DashboardTransition(Transition):
    def __init__(self, message_template: str, transitions: Optional[Dict[str, str]] = None,  format_args: Optional[ClassMapping] = None, upload_params: Optional[ClassMapping] = None):
        super().__init__(message_template, format_args, upload_params)
        self.transitions = transitions

    def execute(self, response: str):
        dashboard_response = response.body_content.lower().strip()
        next_step = self.transitions.get(
            dashboard_response, "new_participation")
        return next_step


class ServerTransition(Transition):
    def __init__(self, transitions: Dict[bool, str], message_template: str, action: Optional[Callable] = None, format_args: Optional[ClassMapping] = None, upload_params: Optional[ClassMapping] = None):
        super().__init__(message_template, format_args, upload_params)
        self.transitions = transitions
        self.action = action

    def execute(self, participation: Participation):
        if not self.transitions:
            return None
        api_response = True  # Simulated API response
        print("sending api call to:", self.action)
        next_step = self.transitions.get(api_response, participation.flow)
        return next_step
