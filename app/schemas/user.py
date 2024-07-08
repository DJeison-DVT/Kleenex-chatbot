from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import date

from app.chatbot.steps import Steps


class UserCreation(BaseModel):
    phone: str


class User(BaseModel):
    id: str = Field(..., alias="_id")
    phone: str
    terms: Optional[bool] = False
    name: Optional[str] = None
    email: Optional[str] = None
    flow_step: str = Steps.ONBOARDING.value
    submissions: Dict[date, int] = Field(default_factory=dict)

    def to_dict(self):
        return {
            "_id": self.id,
            "phone": self.phone,
            "terms": self.terms,
            "name": self.name,
            "email": self.email,
            "flow_step": self.flow_step,
            "submissions": {str(k): v for k, v in self.submissions.items()}
        }
