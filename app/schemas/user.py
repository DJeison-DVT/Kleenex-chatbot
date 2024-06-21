from pydantic import BaseModel, EmailStr

class UserCreation(BaseModel):
    phone: str
    terms: bool = False

class User(BaseModel):
    phone: str
    terms: bool = False
    name: str | None = None
    email: EmailStr | None = None
    flow_step: str = "onboarding"