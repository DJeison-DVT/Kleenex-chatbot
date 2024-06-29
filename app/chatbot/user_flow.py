import re
from typing import Dict, Optional, Tuple, List
from abc import ABC, abstractmethod
from twilio.rest import Client
from fastapi import HTTPException
from httpx import AsyncClient
from collections import defaultdict

from app.schemas.user import User
from app.schemas.participation import Participation
from app.chatbot.messages import Message, send_message
from app.chatbot.steps import Steps
from app.helpers.users import update_user, get_user
from app.helpers.participation import get_current_ticket_number, get_participation_by_phone, update_participation

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
    def execute(self, user: User, message: Optional[Message] = None, response: Optional[str] = None) -> str:
        pass

    def get_template(self) -> str:
        return self.message_template

    async def save_upload_params(self, client: AsyncClient, message: Optional[Message] = None, response: Optional[str] = None):
        user_phone = message.from_number if message else response.from_number
        print("uploading...")
        
        for obj, params in self.upload_params.map.items():
            if obj == User and message.body_content:
                for param in params:
                    print(f"Saving {obj} with {param} as {message.body_content}")
                    user = await get_user(client, user_phone)
                    print(user)
                    print("changing:", param, "to:", message.body_content)
                    setattr(user, param, message.body_content)
                    user = await update_user(client, user)
                    return user
            elif obj == Participation and message.body_content:
                for param in params:
                    participation = await get_participation_by_phone(client, user_phone)
                    setattr(participation, param, message.body_content)
                    await update_participation(client, participation)
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

    def execute(self, user: User, message: Message):
        user_response = re.sub(r'[^\x00-\x7F]+', '', message.body_content).lower().strip()

        next_step = self.transitions.get(user_response, user.flow_step)
        if user_response == "si acepto":
            message.body_content = True
        elif user_response == "no acepto":
            message.body_content = False
        
        if next_step == user.flow_step:
            message.body_content = None
        return next_step


class ResponseIndependentTransition(WhatsAppTransition):
    def __init__(self, next_step: str, message_template: str, format_args: Optional[ClassMapping] = None, upload_params: Optional[ClassMapping] = None):
        super().__init__(message_template, format_args, upload_params)
        self.next_step = next_step

    def execute(self, user: User, message: Message):
        return self.next_step


class MultimediaUploadTransition(WhatsAppTransition):
    def __init__(self, success_step: str, failure_step: str, message_template: str, format_args: Optional[ClassMapping] = None, upload_params: Optional[ClassMapping] = None):
        super().__init__(message_template, format_args, upload_params)
        self.success_step = success_step
        self.failure_step = failure_step

    def execute(self, user: User, message: Message):
        if message.num_media > 0:
            return self.success_step
        return self.failure_step


class DashboardTransition(Transition):
    def __init__(self, message_template: str, transitions: Optional[Dict[str, str]] = None,  format_args: Optional[ClassMapping] = None, upload_params: Optional[ClassMapping] = None):
        super().__init__(message_template, format_args, upload_params)
        self.transitions = transitions

    def execute(self, user: User, response: str):
        dashboard_response = response.body_content.lower().strip()
        next_step = self.transitions.get(
            dashboard_response, "new_participation")
        return next_step


class ServerTransition(Transition):
    def __init__(self, transitions: Dict[bool, str], message_template: str, api_endpoint: Optional[str] = None, format_args: Optional[ClassMapping] = None, upload_params: Optional[ClassMapping] = None):
        super().__init__(message_template, format_args, upload_params)
        self.transitions = transitions
        self.api_endpoint = api_endpoint

    def execute(self, user: User):
        if not self.transitions:
            return None
        api_response = True  # Simulated API response
        print("sending api call to:", self.api_endpoint)
        next_step = self.transitions.get(api_response, user.flow_step)
        return next_step


class FlowManager:
    def __init__(self, flow: Dict[Steps, Transition], user: User):
        self.flow = flow
        self.user = user

    async def update_user_flow(self, httpx_client: AsyncClient, next_step: Steps):
        self.user.flow_step = next_step.value
        await update_user(httpx_client, self.user)

    async def handle_message(self, client: Client, httpx_client: AsyncClient, transition: Transition):
        print("Current transition", transition)
        body = transition.get_template()
        format_args = transition.format_args
        if format_args:
            count = 1
            args = {}
            objects = format_args.available()
            for obj in objects:
                for param in format_args.get(obj):
                    if obj == User:
                        args[str(count)] = f"{self.user.__getattribute__(param)}"
                    elif obj == "other":
                        if param == "current_participations":
                            count = await get_current_ticket_number(httpx_client)
                            args[str(count)] = str(count)
                            print("current participations:", args[str(count)])
                    else:
                        args[str(count)] = f"{param}"
                    count += 1
            
            format_args = args

        try:
            send_message(client, body, self.user, format_args)
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
                if transition.upload_params:
                    await self.handle_upload_params(httpx_client, transition, message)
        elif isinstance(transition, DashboardTransition):
            if response:
                print("Handling response")
                next_step = transition.execute(self.user, response)
                if transition.upload_params:
                    await self.handle_upload_params(httpx_client, transition, response)

        transition = self.flow.get(Steps(next_step), transition)

        if isinstance(transition, ServerTransition):
            print("Handling server transition")
            next_step = transition.execute(self.user)
            await self.update_user_flow(httpx_client, next_step)
            await self.handle_message(client, httpx_client, transition)
            await self.execute(client, httpx_client, response=next_step)
        else:
            print("Handling normal transition")
            await self.handle_message(client, httpx_client, transition)
            await self.update_user_flow(httpx_client, next_step)
