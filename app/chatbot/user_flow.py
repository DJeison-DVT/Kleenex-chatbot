from typing import Dict, Optional
from datetime import datetime

from app.schemas.user import User, UserCreation
from app.schemas.participation import Participation, Status
from app.schemas.prize import Code
from app.chatbot.messages import Message, send_message
from app.chatbot.steps import Steps
from app.core.services.users import create_user, fetch_user_by_phone, can_participate
from app.core.services.participations import ParticipationCreation, create_participation, fetch_participations, update_participation, upload_attempt
from app.core.services.priority_number import count_participations
from app.core.services.codes import get_code_by_participation
from app.core.services.messages import save_message
from app.chatbot.transitions import Transition, WhatsAppTransition, DashboardTransition, ServerTransition, MultimediaUploadTransition
from app.chatbot.flow import FLOW


async def get_current_participation(user: User) -> Participation:
    participations = await fetch_participations(phone=user.phone, status=Status.INCOMPLETE.value, date=datetime.now())
    if isinstance(participations, list):
        participation = participations[0] if participations else None
    if not participation:
        new_participation = ParticipationCreation(user=user)
        participation = await create_participation(new_participation)

    return participation


async def handle_user(user: User, participation: Participation, message: Message):
    flow_manager = FlowManager(FLOW, user, participation)
    try:
        await flow_manager.execute(message=message)
    except Exception as e:
        print(e)
        raise e


async def handle_new_user(message: Message):
    user_creation = UserCreation(phone=message.from_number)
    user = await create_user(user_creation)
    count = await count_participations()

    await send_message(
        FLOW[Steps.ONBOARDING].message_template,
        user,
        {"1": str(count)}
    )


async def handle_max_participations(user: User):
    await send_message(
        FLOW[Steps.MAX_PARTICIPATIONS].message_template,
        user
    )


async def handle_flow(message: Message):
    try:
        user = await fetch_user_by_phone(message.from_number)

        await save_message(message.sms_message_sid, user, from_user=True)

        if not can_participate(user):
            await handle_max_participations(user)
        else:
            participation = await get_current_participation(user)
            await handle_user(user, participation, message)
    except ValueError as e:
        if "User not found" in str(e):
            await handle_new_user(message)
        else:
            print(e)
            raise e


class FlowManager:
    def __init__(self, flow: Dict[Steps, Transition], user: User, participation: Participation):
        self.flow = flow
        self.user = user
        self.participation = participation

    async def update_user_flow(self, next_step: str):
        self.participation.flow = next_step.value
        await update_participation(self.participation.id, self.participation)

    async def handle_message(self, transition: Transition):
        body = transition.get_template()
        format_args = transition.format_args
        if format_args:
            count = 1
            args = {}
            objects = format_args.available()
            for obj in objects:
                for param in format_args.get(obj):
                    if obj == User:
                        args[str(count)
                             ] = f"{self.user.__getattribute__(param)}"
                    elif obj == Participation:
                        args[str(
                            count)] = f"{self.participation.__getattribute__(param)}"
                    elif obj == Code:
                        code = await get_code_by_participation(self.participation)
                        args[str(count)] = f"{code.__getattribute__(param)}"
                    elif obj == "other":
                        if param == "current_participations":
                            ticket_count = await count_participations()
                            args[str(count)] = str(ticket_count)
                    else:
                        args[str(count)] = f"{param}"
                    count += 1

            format_args = args

        try:
            await send_message(body, self.user, format_args)
        except Exception as e:
            print(f"Failed to send message: {str(e)}")

    async def handle_upload_params(self,  transition, message: Optional[Message] = None, response: Optional[str] = None):
        if transition.upload_params:
            content = message.body_content if message else response
            object = await transition.save_upload_params(self.user, self.participation, content)
            if isinstance(object, User):
                self.user = object

    async def execute(self, message: Optional[Message] = None, response: Optional[str] = None):
        step = Steps(self.participation.flow)
        transition = self.flow.get(step, None)
        if not transition:
            raise ValueError("Invalid step")

        next_step = step
        if isinstance(transition, WhatsAppTransition):
            if message:
                next_step = transition.execute(
                    participation=self.participation, message=message)
                if isinstance(transition, MultimediaUploadTransition):
                    print("updload media")
                    await upload_attempt(self.participation)
                if transition.upload_params:
                    await self.handle_upload_params(transition=transition, message=message)
        elif isinstance(transition, DashboardTransition):
            if response and isinstance(response, str):
                next_step = await transition.execute(
                    participation=self.participation, response=response)
                if transition.upload_params:
                    await self.handle_upload_params(transition=transition, response=response)

        transition = self.flow.get(Steps(next_step), transition)

        if isinstance(transition, ServerTransition):
            old_step = next_step
            next_step = await transition.execute(participation=self.participation)
            await self.update_user_flow(next_step or old_step)
            await self.handle_message(transition)
            if next_step:
                await self.execute(response=next_step)
        elif isinstance(transition, DashboardTransition):
            await self.handle_message(transition)
            await self.update_user_flow(next_step)
        else:
            await self.handle_message(transition)
            await self.update_user_flow(next_step)
