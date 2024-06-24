from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticDatabase
from odmantic import AIOEngine

from app.core.config import settings


class _MongoClientSingleton:
    mongo_client: AsyncIOMotorClient | None
    engine: AIOEngine

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(_MongoClientSingleton, cls).__new__(cls)
            cls.instance.mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
            cls.instance.database = cls.instance.mongo_client[settings.MONGO_DATABASE]
            cls.instance.user_collection = cls.instance.database.user
            cls.instance.participant_collection = cls.instance.database.participant
        return cls.instance


def MongoDatabase() -> AgnosticDatabase:
    return _MongoClientSingleton().mongo_client[settings.MONGO_DATABASE]


def UserCollection() -> AgnosticDatabase:
    return _MongoClientSingleton().user_collection


def ParticipantCollection() -> AgnosticDatabase:
    return _MongoClientSingleton().participant_collection


async def ping():
    await MongoDatabase().command("ping")
