from typing import Dict, Optional, Tuple, List 
from abc import ABC, abstractmethod
from twilio.rest import Client
from fastapi import HTTPException
from httpx import AsyncClient

from app.schemas.user import User
from app.chatbot.messages import Message, send_message
from app.chatbot.steps import Steps
from app.helpers.users import update_user, get_user
from app.helpers.participation import get_participation_by_phone, update_participation


from abc import ABC, abstractmethod
from typing import Optional, Dict


class Transition(ABC):
    def __init__(self, message_template: str, format_args: Optional[List[str]] = None, upload_params: Optional[List[Tuple[str, str]]] = None):
        self.message_template = message_template
        self.format_args = format_args
        self.upload_params = upload_params

    @abstractmethod
    def execute(self, user: User, message: Optional[Message] = None, response: Optional[str] = None) -> str:
        pass

    def get_template(self) -> str:
        print(self.format_args)
        return self.message_template

    async def save_upload_params(self, client: AsyncClient, message: Optional[Message] = None, response: Optional[str] = None):
        user_phone = message.from_number if message else response.from_number
        print("uploading...")
        for obj, param in self.upload_params:
            if obj == "user" and message.body_content:
                print(f"Saving {obj} with {param} as {message.body_content}")
                user = await get_user(client, user_phone)
                print(user)
                print("changing:", param, "to:", message.body_content)
                setattr(user, param, message.body_content)
                user = await update_user(client, user)
                return user
            elif obj == "participation" and message.body_content:
                participation = await get_participation_by_phone(client, user_phone)
                setattr(participation, param, message.body_content)
                await update_participation(client, participation)


class WhatsAppTransition(Transition):
    def __init__(self, message_template: str, format_args: Optional[Dict[str, str]] = None, params_to_save: Optional[List[Tuple[str, str]]] = None):
        super().__init__(message_template, format_args, params_to_save)


class ResponseDependentTransition(WhatsAppTransition):
    def __init__(self, transitions: Dict[str, str], message_template: str, format_args: Optional[List[str]] = None, upload_params: Optional[List[Tuple[str, str]]] = None):
        super().__init__(message_template, format_args, upload_params)
        self.transitions = transitions

    def execute(self, user: User, message: Message):
        user_response = message.body_content.lower().strip()

        next_step = self.transitions.get(user_response, user.flow_step)
        if user_response == "si acepto":
            message.body_content = True
        elif user_response == "no acepto":
            message.body_content = False
        
        if next_step == user.flow_step:
            message.body_content = None
        return next_step


class ResponseIndependentTransition(WhatsAppTransition):
    def __init__(self, next_step: str, message_template: str, format_args: Optional[List[str]] = None, upload_params: Optional[List[Tuple[str, str]]] = None):
        super().__init__(message_template, format_args, upload_params)
        self.next_step = next_step

    def execute(self, user: User, message: Message):
        return self.next_step


class MultimediaUploadTransition(WhatsAppTransition):
    def __init__(self, success_step: str, failure_step: str, message_template: str, format_args: Optional[List[str]] = None, upload_params: Optional[List[Tuple[str, str]]] = None):
        super().__init__(message_template, format_args, upload_params)
        self.success_step = success_step
        self.failure_step = failure_step

    def execute(self, user: User, message: Message):
        if message.num_media > 0:
            return self.success_step
        return self.failure_step


class DashboardTransition(Transition):
    def __init__(self, message_template: str, transitions: Optional[Dict[str, str]] = None,  format_args: Optional[List[str]] = None, upload_params: Optional[List[Tuple[str, str]]] = None):
        super().__init__(message_template, format_args, upload_params)
        self.transitions = transitions

    def execute(self, user: User, response: Message):
        dashboard_response = response.body_content.lower().strip()
        next_step = self.transitions.get(
            dashboard_response, "new_participation")
        return next_step


class ServerTransition(Transition):
    def __init__(self, transitions: Dict[bool, str], message_template: str, api_endpoint: Optional[str] = None, format_args: Optional[List[str]] = None, upload_params: Optional[List[Tuple[str, str]]] = None):
        super().__init__(message_template, format_args, upload_params)
        self.transitions = transitions
        self.api_endpoint = api_endpoint

    def execute(self, user: User):
        if not self.transitions:
            return None
        api_response = True  # Simulated API response
        next_step = self.transitions.get(api_response, user.flow_step)
        return next_step


class FlowManager:
    def __init__(self, flow: Dict[Steps, Transition], user: User):
        self.flow = flow
        self.user = user

    async def update_user_flow(self, httpx_client: AsyncClient, next_step: Steps):
        self.user.flow_step = next_step.value
        await update_user(httpx_client, self.user)

    def handle_message(self, client: Client, body: str):
        print("sending message")
        try:
            send_message(client, body, self.user)
        except Exception as e:
            print(f"Failed to send message: {str(e)}")

    async def handle_upload_params(self, client: AsyncClient, transition, message: Optional[Message] = None, response: Optional[str] = None):
        if transition.upload_params:
            sending = message if message else response
            object = await transition.save_upload_params(client, sending)
            if isinstance(object, User):
                self.user = object

    async def execute(self, client: Client, httpx_client: AsyncClient, message: Optional[Message] = None, response: Optional[str] = None):
        step = Steps(self.user.flow_step)
        print(step)

        transition = self.flow.get(step, None)
        if not transition:
            raise HTTPException(status_code=500, detail="Invalid flow step")

        print("current transition:", transition)

        if isinstance(transition, WhatsAppTransition):
            if message:
                print("handling message")
                next_step = transition.execute(self.user, message)
                print("Uploading:", transition.upload_params, message.body_content)
                await self.handle_upload_params(httpx_client, transition, message)
        elif isinstance(transition, DashboardTransition):
            if response:
                print("Handling response")
                next_step = transition.execute(self.user, response)
                await self.handle_upload_params(httpx_client, transition, response)

        transition = self.flow.get(Steps(next_step), transition)

        if isinstance(transition, ServerTransition):
            print("Handling server transition")
            next_step = transition.execute(self.user)
            await self.update_user_flow(httpx_client, next_step)
            self.handle_message(client, transition.get_template())
            await self.execute(client, httpx_client, response=next_step)
        else:
            print("Handling normal transition")
            self.handle_message(client, transition.get_template())
            print(f"Next step: {next_step}")
            await self.update_user_flow(httpx_client, next_step)
