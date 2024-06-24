from fastapi import FastAPI
# from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.api import api_router


@asynccontextmanager
async def app_init(app: FastAPI):
    app.include_router(api_router, prefix=settings.API_STR)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=app_init,
)

# Set all CORS enabled origins
# if settings.BACKEND_CORS_ORIGINS:
#     app.add_middleware(
#         CORSMiddleware,
#         # Trailing slash causes CORS failures from these supported domains
#         allow_origins=[str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS], # noqa
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )


@app.get("/")
async def read_root():
    return {"message": "Hello World", "prefix": settings.API_STR}
