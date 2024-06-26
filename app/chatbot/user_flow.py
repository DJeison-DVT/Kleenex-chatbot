from typing import Dict, Optional
from abc import ABC, abstractmethod
from httpx import AsyncClient

from app.schemas.user import User
from app.chatbot.messages import Message, send_message
from app.chatbot.steps import Steps


class Transition(ABC):
    @abstractmethod
    def execute(self, user: User, message: Optional[Message] = None, response: Optional[str] = None) -> str:
        pass


class ResponseDependentTransition(Transition):
    def __init__(self, transitions: Dict[str, str], message_template: str, format_args: Optional[Dict[str, str]] = None):
        self.transitions = transitions
        self.message_template = message_template
        self.format_args = format_args

    def execute(self, user, message: Message):
        user_response = message.body_content.lower().strip()
        next_step = self.transitions.get(user_response, user.flow_step)
        return next_step


class ResponseIndependentTransition(Transition):
    def __init__(self, next_step: str, message_template: str, format_args: Optional[Dict[str, str]] = None):
        self.next_step = next_step
        self.message_template = message_template
        self.format_args = format_args

    def execute(self, user, message: Message):
        return self.next_step


class MultimediaUploadTransition(Transition):
    def __init__(self, success_step: str, failure_step: str, message_template: str, format_args: Optional[Dict[str, str]] = None):
        self.success_step = success_step
        self.failure_step = failure_step
        self.message_template = message_template
        self.format_args = format_args

    def execute(self, user, message: Message):
        if message.num_media > 0:
            return self.success_step
        return self.failure_step


class DashboardTransition(Transition):
    def __init__(self, transitions: Dict[str, str], message_template: str, format_args: Optional[Dict[str, str]] = None):
        self.transitions = transitions
        self.message_template = message_template
        self.format_args = format_args

    def execute(self, user, response: str):
        dashboard_response = response.body_content.lower().strip()
        next_step = self.transitions.get(dashboard_response, user.flow_step)
        return next_step


class ServerTransition(Transition):
    def __init__(self, transitions, message_template: str, format_args: Optional[Dict[str, str]] = None):
        self.message_template = message_template
        self.format_args = format_args
        self.transitions = transitions

    def execute(self, user):
        # api call and transition
        if not self.transitions:
            return None
        api_response = True
        next_step = self.transitions.get(api_response, user.flow_step)
        return next_step


class FlowManager:
    def __init__(self, flow: Dict[Steps, Transition], user: User):
        self.flow = flow
        self.user = User(**user)

    def update_flow(self, next_transition: str):
        # api call and transition
        pass

    def handle_message(self, client: AsyncClient, message: Message, body: str):
        send_message(self.client, message, body)

    def execute(self, client: AsyncClient, message: Message):
        transition = self.flow.get(self.user.flow_step, None)
        print(f"Transition: {transition}")
