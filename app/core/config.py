from pathlib import Path
from pydantic import AnyHttpUrl, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated, Any


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


def get_env_path():
    path = Path(__file__).resolve().parent.parent.parent / ".env"
    print(path)
    return path


class Settings(BaseSettings):
    API_STR: str = "/api"
    BASE_URL: str
    USER_SECTION: str = "/users"
    PARTICIPATION_SECTION: str = "/participations"
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyHttpUrl] | str, BeforeValidator(parse_cors)
    ] = []
    MONGO_URI: str
    MONGO_DATABASE: str
    PROJECT_NAME: str = "Kleenex Chatbot API"
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_MESSAGING_SERVICE_SID: str

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8')

    DEBUG: bool = False

settings = Settings()
