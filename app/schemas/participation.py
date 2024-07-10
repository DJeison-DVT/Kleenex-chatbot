from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

from app.chatbot.steps import Steps
from app.schemas.user import User


class Status(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    REJECTED = "REJECTED"
    APPROVED = "APPROVED"
    FULLFILED = "FULLFILED"


class ParticipationCreation(BaseModel):
    user: User


class Participation(BaseModel):
    id: str = Field(..., alias="_id")
    user: User
    ticket_url: Optional[str] = None
    ticket_attempts: int = 0
    priority_number: int = -1
    datetime: datetime
    status: Status = Status.INCOMPLETE
    prize: Optional[str] = None
    flow: str = Steps.ONBOARDING.value

    def to_dict(self):
        return {
            "_id": self.id,
            "user": self.user.to_dict(),
            "ticket_url": self.ticket_url,
            "ticket_attempts": self.ticket_attempts,
            "priority_number": self.priority_number,
            "datetime": self.datetime,
            "status": self.status,
            "prize": self.prize,
            "flow": self.flow
        }
