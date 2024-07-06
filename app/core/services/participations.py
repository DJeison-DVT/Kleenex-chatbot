from datetime import datetime, timedelta, timezone
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from bson import ObjectId
from pymongo.errors import InvalidDocument

from app.schemas.participation import Participation, Status, ParticipationCreation
from app.db.db import ParticipationsCollection


async def fetch_participations(
    limit: int = 10,
    date: Optional[datetime] = None,
    phone: Optional[str] = None,
    status: Optional[str] = None
) -> List[Participation]:
    query = {}

    if date:
        start_of_day = datetime(date.year, date.month, date.day)
        end_of_day = start_of_day + timedelta(days=1)
        query["datetime"] = {"$gte": start_of_day, "$lt": end_of_day}

    if phone:
        query["user.phone"] = phone

    if status:
        query["status"] = status

    cursor = ParticipationsCollection().find(query).sort(
        "datetime", ASCENDING).limit(limit)
    participations = []
    async for participation in cursor:
        participation["_id"] = str(participation["_id"])
        participations.append(Participation(**participation))

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


async def count_participations(date: datetime = datetime.now(timezone.utc).date()) -> int:
    start_of_day = datetime(
        date.year,
        date.month,
        date.day,
        tzinfo=timezone.utc
    )
    end_of_day = start_of_day + timedelta(days=1)
    query = {
        "datetime": {"$gte": start_of_day, "$lt": end_of_day},
        "status": {"$ne": Status.INCOMPLETE.value}
    }
    return await ParticipationsCollection().count_documents(query)


async def create_participation(
    participation: ParticipationCreation,
):
    user = participation.user.to_dict()

    if not user:
        raise ValueError("User is required")

    try:
        result = await ParticipationsCollection().insert_one({
            "datetime": datetime.now(),
            "user": user,
            "status": Status.INCOMPLETE.value,
        })
    except InvalidDocument as e:
        raise InvalidDocument(e)
    except Exception as e:
        if hasattr(e, 'code') and e.code == 11000:
            raise ValueError("Participation already exists")
        raise e

    new_participation = await ParticipationsCollection().find_one({"_id": result.inserted_id})
    # Convert ObjectId to string
    new_participation["_id"] = str(new_participation["_id"])
    return Participation(**new_participation)


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
