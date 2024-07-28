from pydantic import BaseModel


class User(BaseModel):
    username: str | None = None
    role: str | None = None


class UserInDB(User):
    hashed_password: str | None = None


class Token(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None


class TokenData(BaseModel):
    username: str | None = None
