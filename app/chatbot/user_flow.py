from typing import Dict, Optional
from datetime import datetime

from app.schemas.user import User, UserCreation
from app.schemas.participation import Participation, Status
from app.chatbot.messages import Message, send_message
from app.chatbot.steps import Steps
from app.core.services.users import update_user_by_phone, create_user, fetch_user_by_phone, can_participate
from app.core.services.participations import ParticipationCreation, create_participation, fetch_participations, update_participation
from app.core.services.priority_number import count_participations
from app.chatbot.transitions import Transition, WhatsAppTransition, DashboardTransition, ServerTransition
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

    send_message(
        FLOW[Steps.ONBOARDING].message_template,
        user,
        {"1": str(count)}
    )


def handle_max_participations(user: User):
    send_message(
        FLOW[Steps.MAX_PARTICIPATIONS].message_template,
        user
    )


async def handle_flow(message: Message):
    try:
        user = await fetch_user_by_phone(message.from_number)
        if not can_participate(user):
            handle_max_participations(user)
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
                        args[str(count)
                             ] = f"{self.user.__getattribute__(param)}"
                    elif obj == Participation:
                        args[str(
                            count)] = f"{self.participation.__getattribute__(param)}"
                    elif obj == "other":
                        if param == "current_participations":
                            ticket_count = await count_participations()
                            args[str(count)] = str(ticket_count)
                    else:
                        args[str(count)] = f"{param}"
                    count += 1

            format_args = args

        try:
            send_message(body, self.user, format_args)
        except Exception as e:
            print(f"Failed to send message: {str(e)}")

    async def handle_upload_params(self,  transition, message: Optional[Message] = None, response: Optional[str] = None):
        if transition.upload_params:
            sending = message if message else response
            object = await transition.save_upload_params(sending)
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
                print("Uploading:", transition.upload_params,
                      message.body_content)
                if transition.upload_params:
                    await self.handle_upload_params(transition=transition, message=message)
        elif isinstance(transition, DashboardTransition):
            if response:
                print("Handling response")
                next_step = transition.execute(response=response)
                if transition.upload_params:
                    await self.handle_upload_params(transition=transition, response=response)

        transition = self.flow.get(Steps(next_step), transition)

        if isinstance(transition, ServerTransition):
            print("Handling server transition")
            # sleep for 3 sec
            next_step = await transition.execute(participation=self.participation)
            if not next_step:
                await self.handle_message(transition)
            else:
                await self.update_user_flow(next_step)
                await self.handle_message(transition)
                await self.execute(response=next_step)
        elif isinstance(transition, DashboardTransition):
            print("Handling dashboard transition")
        else:
            print("Handling normal transition")
            await self.handle_message(transition)
            await self.update_user_flow(next_step)
