from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.api import api_router
from app.chatbot.endpoint import router as chatbot_router


load_dotenv()


@asynccontextmanager
async def app_init(app: FastAPI):
    app.include_router(api_router, prefix=settings.API_STR)
    app.include_router(chatbot_router, prefix="/chatbot")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=app_init,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def read_root():
    return {"message": "Hello World", "prefix": settings.API_STR}
