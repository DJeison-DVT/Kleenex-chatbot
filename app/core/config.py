import os
from pydantic import AnyHttpUrl, BeforeValidator
from pydantic_settings import BaseSettings
from typing import Annotated, Any
from pathlib import Path


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)

class Settings(BaseSettings):
    API_STR: str = "/api"
    PROJECT_NAME: str = "Kleenex Chatbot API"
    MONGO_URI: str 
    MONGO_DATABASE: str
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyHttpUrl] | str, BeforeValidator(parse_cors)
    ] = []

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
settings = Settings()