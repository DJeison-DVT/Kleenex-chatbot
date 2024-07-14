from datetime import datetime
from bson import ObjectId
from typing import Dict

from app.db.db import _MongoClientSingleton, ParticipationsCollection, CountersCollection, PrizesCollection
from app.schemas.participation import Participation, Status


async def count_participations(date: datetime = datetime.now()) -> int:
    date = date.strftime("%Y-%m-%d")
    count = await CountersCollection().find_one({"_id": date})
    return count["value"] if count else 0


async def get_prize(priority_number: int, date: datetime, session) -> Dict:
    date = date.strftime("%Y-%m-%d")
    prize = await PrizesCollection().find_one_and_update(
        {"priority_number": priority_number, "date": date, "taken": False},
        {"$set": {"taken": True}},
        session=session,
    )
    return prize["prize"] if prize else None


async def set_priority_number(participation: Participation):
    today = datetime.now().strftime("%Y-%m-%d")
    priority_number = -1
    async with await _MongoClientSingleton().mongo_client.start_session() as session:
        async with session.start_transaction():
            try:
                result = await CountersCollection().find_one_and_update(
                    {"_id": today},
                    {"$inc": {"value": 1}},
                    upsert=True,
                    session=session,
                    return_document=True
                )
                priority_number = result["value"]
                participation.priority_number = priority_number
                participation.status = Status.COMPLETE.value
                participation.prize = await get_prize(priority_number, today, session)

                object_id = ObjectId(participation.id)
                updated_participation = participation.to_dict()
                updated_participation.pop("_id", None)

                await ParticipationsCollection().update_one(
                    {"_id": object_id},
                    {"$set": updated_participation},
                    session=session
                )

            except Exception as e:
                await session.abort_transaction()
                raise e

    return bool(participation.prize)
