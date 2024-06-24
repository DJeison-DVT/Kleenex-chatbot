from pydantic import BaseModel, EmailStr, Field
from app.chatbot.steps import Steps


class UserCreation(BaseModel):
    phone: str
    terms: bool = False


class User(BaseModel):
    id: str = Field(..., alias="_id")
    phone: str
    terms: bool = False
    name: str | None = None
    email: EmailStr | None = None
    flow_step: str = Steps.ONBOARDING.value
