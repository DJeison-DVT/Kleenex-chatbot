from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Optional
from datetime import date

from app.chatbot.steps import Steps


class UserCreation(BaseModel):
    phone: str
    terms: bool = False


class User(BaseModel):
    id: str = Field(..., alias="_id")
    phone: str
    terms: Optional[bool] = False
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    flow_step: str = Steps.ONBOARDING.value
    submissions: Dict[date, int] = Field(default_factory=dict)
