from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticDatabase
from odmantic import AIOEngine

from app.core.config import settings


class _MongoClientSingleton:
    mongo_client: AsyncIOMotorClient | None = None
    engine: AIOEngine | None = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(_MongoClientSingleton, cls).__new__(cls)
            cls.instance.mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
            cls.instance.database = cls.instance.mongo_client[settings.MONGO_DATABASE]
        return cls.instance


def MongoDatabase() -> AgnosticDatabase:
    return _MongoClientSingleton().mongo_client[settings.MONGO_DATABASE]


def UsersCollection() -> AgnosticDatabase:
    return MongoDatabase().users


def ParticipationsCollection() -> AgnosticDatabase:
    # datetime is stored in UTC, offset -6 for mexico
    return MongoDatabase().participations


def CountersCollection() -> AgnosticDatabase:
    return MongoDatabase().counters


def PrizesCollection() -> AgnosticDatabase:
    return MongoDatabase().prizes


def PrizeCodesCollection() -> AgnosticDatabase:
    return MongoDatabase().codes


def DashboardUsersCollection() -> AgnosticDatabase:
    return MongoDatabase().dashboard_users


def CodeCountersCollection() -> AgnosticDatabase:
    return MongoDatabase().prize_counters


def MessagesCollection() -> AgnosticDatabase:
    # timestamp is stored in UTC, offset -6 for mexico
    return MongoDatabase().messages


def ParticipationLogs() -> AgnosticDatabase:
    return MongoDatabase().participation_logs


async def ping():
    await MongoDatabase().command("ping")
