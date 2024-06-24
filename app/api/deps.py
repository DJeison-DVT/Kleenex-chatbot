from app.db.db import MongoDatabase
from typing import Generator


def get_db() -> Generator:
    try:
        db = MongoDatabase()
        yield db
    finally:
        pass
