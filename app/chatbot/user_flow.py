from typing import Dict, Optional
from abc import ABC, abstractmethod
from twilio.rest import Client
from fastapi import HTTPException
from httpx import AsyncClient

from app.schemas.user import User
from app.chatbot.messages import Message, send_message
from app.chatbot.steps import Steps
from app.helpers.users import update_user


from abc import ABC, abstractmethod
from typing import Optional, Dict


class Transition(ABC):
    def __init__(self, message_template: str, format_args: Optional[Dict[str, str]] = None):
        self.message_template = message_template
        self.format_args = format_args

    @abstractmethod
    def execute(self, user: User, message: Optional[Message] = None, response: Optional[str] = None) -> str:
        pass

    def get_template(self) -> str:
        return self.message_template


class ResponseDependentTransition(Transition):
    def __init__(self, transitions: Dict[str, str], message_template: str, format_args: Optional[Dict[str, str]] = None):
        super().__init__(message_template, format_args)
        self.transitions = transitions

    def execute(self, user: User, message: Message):
        print("Executing response dependent transition...")
        user_response = message.body_content.lower().strip()

        print(self.transitions)
        next_step = self.transitions.get(user_response, user.flow_step)
        print(next_step)
        return next_step


class ResponseIndependentTransition(Transition):
    def __init__(self, next_step: str, message_template: str, format_args: Optional[Dict[str, str]] = None):
        super().__init__(message_template, format_args)
        self.next_step = next_step

    def execute(self, user: User, message: Message):
        print("Executing response independent transition...")
        return self.next_step


class MultimediaUploadTransition(Transition):
    def __init__(self, success_step: str, failure_step: str, message_template: str, format_args: Optional[Dict[str, str]] = None):
        super().__init__(message_template, format_args)
        self.success_step = success_step
        self.failure_step = failure_step

    def execute(self, user: User, message: Message):
        print("Executing multimedia upload transition...")
        if message.num_media > 0:
            return self.success_step
        return self.failure_step


class DashboardTransition(Transition):
    def __init__(self, transitions: Dict[str, str], message_template: str, format_args: Optional[Dict[str, str]] = None):
        super().__init__(message_template, format_args)
        self.transitions = transitions

    def execute(self, user: User, response: Message):
        print("Executing dashboard transition...")
        dashboard_response = response.body_content.lower().strip()
        next_step = self.transitions.get(dashboard_response, user.flow_step)
        return next_step


class ServerTransition(Transition):
    def __init__(self, transitions: Dict[bool, str], message_template: str, format_args: Optional[Dict[str, str]] = None):
        super().__init__(message_template, format_args)
        self.transitions = transitions

    def execute(self, user: User):
        print("Executing server transition...")
        # Simulated API call and transition logic
        if not self.transitions:
            return None
        api_response = True  # Simulated API response
        next_step = self.transitions.get(api_response, user.flow_step)
        return next_step


class FlowManager:
    def __init__(self, flow: Dict[Steps, Transition], user: User):
        self.flow = flow
        self.user = User(**user)

    async def update_user_flow(self, httpx_client: AsyncClient, next_step: Steps):
        self.user.flow_step = next_step.value
        print(self.user)
        await update_user(httpx_client, self.user)

    def handle_message(self, client: Client, body: str, message: Optional[Message] = None):
        send_message(client, body, message=message)

    async def execute(self, client: Client, httpx_client: AsyncClient, message: Optional[Message] = None, response: Optional[str] = None):
        step = Steps(self.user.flow_step)
        print(step)

        transition = self.flow.get(step, None)
        if not transition:
            raise HTTPException(status_code=500, detail="Invalid flow step")

        if message:
            print("Handling message")
            next_step = transition.execute(self.user, message)
        elif response:
            print("Handling response")
            next_step = transition.execute(self.user, response)

        transition = self.flow.get(Steps(next_step), transition)
        if message:
            self.handle_message(client, transition.get_template(), message)
        await self.update_user_flow(httpx_client, next_step)
