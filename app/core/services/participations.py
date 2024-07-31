from datetime import datetime, timedelta, timezone
from typing import List, Optional
from bson import ObjectId
from pymongo.errors import InvalidDocument
from fastapi import HTTPException
from zoneinfo import ZoneInfo

from app.schemas.participation import Participation, Status, ParticipationCreation
from app.db.db import ParticipationsCollection, PrizeCodesCollection, _MongoClientSingleton, CodeCountersCollection
from app.chatbot.steps import Steps
from app.core.services.users import fetch_user_by_phone, update_user_by_phone
from app.core.config import settings
from app.core.services.datetime_mexico import *


async def fetch_participations(
    limit: Optional[int] = None,
    date: Optional[datetime] = None,
    phone: Optional[str] = None,
    status: Optional[str] = None
) -> List[Participation]:
    query = {}

    if date:
        start_of_day = datetime(date.year, date.month,
                                date.day, tzinfo=settings.LOCAL_TIMEZONE)
        end_of_day = start_of_day + timedelta(days=1)
        start_of_day_utc = start_of_day.astimezone(ZoneInfo("UTC"))
        end_of_day_utc = end_of_day.astimezone(ZoneInfo("UTC"))
        query["datetime"] = {"$gte": start_of_day_utc, "$lt": end_of_day_utc}

    if phone:
        query["user.phone"] = phone

    if status:
        query["status"] = status

    cursor = ParticipationsCollection().find(query)

    if limit:
        cursor = cursor.limit(limit)

    participations = []
    async for participation in cursor:
        participation["_id"] = str(participation["_id"])
        try:
            participation = Participation(**participation)
        except Exception as e:
            raise e
        participations.append(participation)
    return participations


async def fetch_participation_by_id(id: str) -> Participation:
    if not ObjectId.is_valid(id):
        raise ValueError("Invalid ID")
    object_id = ObjectId(id)
    existing_participation = await ParticipationsCollection().find_one({"_id": object_id})
    if not existing_participation:
        raise ValueError("Participation not found")
    existing_participation["_id"] = str(existing_participation["_id"])
    return Participation(**existing_participation)


async def fetch_participation_by_phone(phone: str) -> Participation:
    existing_participation = await ParticipationsCollection().find_one({"user.phone": phone})
    if not existing_participation:
        raise ValueError("Participation not found")
    existing_participation["_id"] = str(existing_participation["_id"])
    return Participation(**existing_participation)


async def count_participations(date: datetime = get_current_datetime().date()) -> int:
    start_of_day_local = datetime(
        date.year, date.month, date.day, tzinfo=settings.LOCAL_TIMEZONE)
    end_of_day_local = start_of_day_local + timedelta(days=1)

    start_of_day_utc = start_of_day_local.astimezone(ZoneInfo("UTC"))
    end_of_day_utc = end_of_day_local.astimezone(ZoneInfo("UTC"))

    query = {
        "datetime": {"$gte": start_of_day_utc, "$lt": end_of_day_utc},
        "status": {"$ne": Status.INCOMPLETE.value}
    }

    return await ParticipationsCollection().count_documents(query)


async def create_participation(
    participation: ParticipationCreation,
):
    user = participation.user.to_dict()

    if not user or not user.get("_id"):
        raise ValueError("User is required")

    flow = Steps.ONBOARDING.value if user.get(
        "complete") == False else Steps.NEW_PARTICIPATION.value

    try:
        result = await ParticipationsCollection().insert_one({
            "datetime": get_current_datetime(),
            "user": user,
            "status": Status.INCOMPLETE.value,
            "flow": flow,
        })
    except InvalidDocument as e:
        raise InvalidDocument(e)
    except Exception as e:
        if hasattr(e, 'code') and e.code == 11000:
            raise ValueError("Participation already exists")
        raise e

    new_participation = await ParticipationsCollection().find_one({"_id": result.inserted_id})
    new_participation["_id"] = str(new_participation["_id"])

    return Participation(**new_participation)


async def accept_participation(participation: Participation, serial_number: str) -> bool:
    id = ObjectId(participation.id)

    if not serial_number:
        return 'rejected'

    if participation.serial_number:
        raise Exception("Serial number already set")

    existing = await ParticipationsCollection().find_one({"serial_number": serial_number})
    if existing:
        raise ValueError("Duplicate Serial Number")

    available_code = await PrizeCodesCollection().find_one({
        "taken": False,
        "amount": int(participation.prize)
    })

    if not available_code:
        raise HTTPException(status_code=404, detail="No available code found")

    async with await _MongoClientSingleton().mongo_client.start_session() as session:
        async with session.start_transaction():
            try:
                participation.serial_number = serial_number
                await ParticipationsCollection().update_one(
                    {"_id": id},
                    {"$set": {
                        "serial_number": serial_number,
                    }}
                )

                await PrizeCodesCollection().update_one(
                    {"_id": available_code['_id']},
                    {"$set": {
                        "participationId": id,
                        "taken": True,
                    }}
                )

                await CodeCountersCollection().update_one(
                    {"_id": int(available_code['amount'])},
                    {"$inc": {
                        "taken": 1,
                        "available": -1
                    }}
                )
            except Exception as e:
                print(e)
                await session.abort_transaction()
                raise e

    return 'accepted'


async def update_participation(id: str, participation: Participation):
    if not ObjectId.is_valid(id):
        raise ValueError("Invalid ID")
    object_id = ObjectId(id)
    new_participation = participation.to_dict()
    new_participation.pop("_id", None)

    await ParticipationsCollection().update_one({"_id": object_id}, {"$set": new_participation})

    updated_participation = await ParticipationsCollection().find_one({"_id": object_id})
    if not updated_participation:
        raise ValueError("Participation not found after update")
    updated_participation["_id"] = str(updated_participation["_id"])
    return Participation(**updated_participation)


async def delete_participation_by_id(id: str):
    if not ObjectId.is_valid(id):
        raise ValueError("Invalid ID")
    object_id = ObjectId(id)

    await ParticipationsCollection().delete_one({"_id": object_id})


async def add_participation(participation: Participation):
    phone = participation.user.phone
    if not phone:
        raise ValueError("Phone number is required")
    user = await fetch_user_by_phone(phone)
    if not user:
        raise ValueError("User not found")

    today = get_current_datetime().strftime("%Y-%m-%d")

    user.submissions[today] = user.submissions.get(today, 0) + 1
    await update_user_by_phone(phone, user)


async def upload_attempt(participation: Participation):
    async with await _MongoClientSingleton().mongo_client.start_session() as session:
        async with session.start_transaction():
            try:
                if not ObjectId.is_valid(participation.id):
                    raise ValueError("Invalid ID")
                object_id = ObjectId(participation.id)

                print(object_id)
                result = await ParticipationsCollection().find_one_and_update(
                    {"_id": object_id},
                    {"$inc": {"ticket_attempts": 1}},
                    session=session,
                    return_document=True
                )

                ticket_attempts = result["ticket_attempts"]
                participation.ticket_attempts = ticket_attempts

                if ticket_attempts >= settings.INVALID_PHOTO_MAX_OPPORTUNITIES:
                    participation.status = Status.REJECTED.value
                    await ParticipationsCollection().update_one(
                        {"_id": object_id},
                        {'$set': {'status': Status.REJECTED.value}},
                        session=session
                    )

            except Exception as e:
                print(e)
                await session.abort_transaction()
                raise e
    return
