from datetime import datetime

from app.db.db import _MongoClientSingleton, MongoDatabase, ParticipationsCollection
from app.schemas.participation import Participation


async def get_priority_number(participation: Participation):
    today = datetime.now().date()
    print(today)
    async with await _MongoClientSingleton().mongo_client.start_session() as session:
        async with session.start_transaction():
            try:
                result = await MongoDatabase().counters.find_one_and_update(
                    {"_id": today},
                    {"$inc": {"value": 1}},
                    upsert=True,
                    session=session,
                    return_document=True
                )
                priority_number = result["value"]
                await ParticipationsCollection().insert_one(
                    {"priority_number": priority_number, **participation.to_dict()},
                    session=session
                )
            except Exception as e:
                await session.abort_transaction()
                raise e
