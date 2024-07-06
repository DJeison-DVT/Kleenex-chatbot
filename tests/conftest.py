from app.main import app
from app.db.init_db import init_db
from app.db.db import MongoDatabase, _MongoClientSingleton
from app.core.config import settings
from fastapi.testclient import TestClient
from typing import Generator
import pytest_asyncio
import asyncio
import pytest


TEST_DATABASE = "test"
settings.MONGO_DATABASE = TEST_DATABASE


@pytest_asyncio.fixture(scope="session")
async def db():
    db = MongoDatabase()
    _MongoClientSingleton.instance.mongo_client.get_io_loop = asyncio.get_event_loop
    await init_db(db)
    yield db
    # await _MongoClientSingleton.instance.mongo_client.drop_database(TEST_DATABASE)


@pytest_asyncio.fixture(scope="function")
async def clean_db(db):
    # Cleanup before each test
    await db.participations.delete_many({})
    await db.users.delete_many({})

    yield
    # Cleanup after each test
    await db.participations.delete_many({})
    await db.users.delete_many({})


@pytest.fixture(scope="session")
def client(db) -> Generator:
    with TestClient(app) as c:
        yield c
