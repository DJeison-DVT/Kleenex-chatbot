import pytest
import asyncio
import pytest_asyncio
from typing import Generator
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.db import MongoDatabase, _MongoClientSingleton
from app.db.init_db import init_db
from app.main import app

TEST_DATABASE = "test"
settings.MONGO_DATABASE = TEST_DATABASE


@pytest_asyncio.fixture(scope="session")
async def db():
    db = MongoDatabase()
    _MongoClientSingleton.instance.mongo_client.get_io_loop = asyncio.get_event_loop
    await init_db(db)
    yield db


@pytest.fixture(scope="session")
def client(db) -> Generator:
    with TestClient(app) as c:
        yield c
