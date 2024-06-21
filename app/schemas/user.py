from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId

class UserCreation(BaseModel):
    phone: str
    terms: bool = False

class User(BaseModel):
    phone: str
    terms: bool = False
    name: str | None = None
    email: EmailStr | None = None
    flow_step: str = "onboarding"