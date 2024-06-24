from typing import Dict, Optional
from abc import ABC, abstractmethod

from app.schemas.user import User
from app.chatbot.steps import Steps


class Transition(ABC):
    @abstractmethod
    def execute(self, user: User, response: Optional[str] = None, **kwargs):
        pass

    @abstractmethod
    def get_next_step(self, result, user: User) -> str:
        pass


# Server transitions
class ServerTransition(Transition):
    @abstractmethod
    def api_call(self, user: User, **kwargs):
        pass

    def execute(self, user: User, **kwargs):
        response = self.api_call(user, **kwargs)
        return response


class MultimediaUploadTransition(ServerTransition):
    def __init__(self, success_step: str, failure_step: str):
        self.success_step = success_step
        self.failure_step = failure_step

    def api_call(self, user: User, **kwargs):
        # TODO
        # Simulate upload and return True if successful, False otherwise
        return False  # Change this to the actual upload logic

    def get_next_step(self, result, user: User):
        return self.success_step if result else self.failure_step


class ResponseDependentTransition(Transition):
    def __init__(self, transitions: Dict[str, str]):
        self.transitions = transitions

    def execute(self, user: User, response: Optional[str] = None, **kwargs):
        return response

    def get_next_step(self, result, user: User):
        return self.transitions.get(result, None)


class ResponseIndependentTransition(Transition):
    def __init__(self, next_step: str):
        self.next_step = next_step

    def execute(self, user: User, **kwargs):
        return ''

    def get_next_step(self, result, user: User):
        return self.next_step


class DashboardTransition(ServerTransition):
    def __init__(self, end_step: str):
        self.end_step = end_step

    def api_call(self, user: User, **kwargs):
        # TODO
        # Simulate an API call to handle dashboard confirmation
        return False

    def get_next_step(self, result, user: User):
        return self.end_step if result else None


class ResponseIndependentTransition(Transition):
    def __init__(self, next_step: str):
        self.next_step = next_step

    def execute(self, **kwargs):
        return ''

    def get_next_step(self, result):
        return self.next_step


class FlowStep:
    def __init__(self, name: str, transition: Transition, is_end: bool = False):
        self.name = name
        self.is_end = is_end
        self.transition = transition

    def execute(self, *args, **kwargs):
        return self.transition.execute(*args, **kwargs)

    def get_next_step(self, result):
        return self.transition.get_next_step(result)


class FlowStep:
    def __init__(self, name: str, transition: Transition, is_end: bool = False):
        self.name = name
        self.is_end = is_end
        self.transition = transition

    def execute(self, user: User, response: Optional[str] = None, **kwargs):
        return self.transition.execute(user, response, **kwargs)

    def get_next_step(self, result, user: User):
        return self.transition.get_next_step(result, user)


class UserFlowManager:
    def __init__(self, user: User, steps: Dict[str, FlowStep]):
        self.user = user
        self.steps = steps
        self.current_step = self.get_user_step()

    def get_user_step(self):
        return self.steps.get(self.user.current_step, self.steps[Steps.ONBOARDING.value])

    def save_user_step(self, step_name: str):
        self.user.current_step = step_name

    def execute_step(self, response: Optional[str] = None, **kwargs):
        step = self.current_step
        result = step.execute(self.user, response, **kwargs)
        next_step = step.get_next_step(result, self.user)
        self.save_user_step(next_step)
        self.current_step = self.steps.get(next_step, None)
        return result
