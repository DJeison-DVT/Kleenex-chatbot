from app.core.config import settings


async def init_db(db) -> None:
    users_collection = db.client[settings.MONGO_DATABASE].users
    await users_collection.create_index("phone", unique=True)
    await users_collection.delete_one({"phone": "1234567890"})
