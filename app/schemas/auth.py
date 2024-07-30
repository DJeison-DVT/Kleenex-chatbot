from pydantic import BaseModel


class DashboardUser(BaseModel):
    username: str | None = None
    role: str | None = None


class DashboardUserCreate(DashboardUser):
    password: str | None = None


class DashboardUserInDB(DashboardUser):
    hashed_password: str | None = None


class Token(BaseModel):
    access_token: str | None = None


class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None
