from app.core.config import settings


async def init_db(db) -> None:
    users_collection = db.client[settings.MONGO_DATABASE].users
    await users_collection.create_index("phone", unique=True)
    participations_collection = db.client[settings.MONGO_DATABASE].participations
