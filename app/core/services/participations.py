from datetime import datetime, timedelta, timezone
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from bson import ObjectId
from pymongo.errors import InvalidDocument

from app.schemas.participation import Participation, Status, ParticipationCreation
from app.db.db import ParticipationsCollection
from app.chatbot.steps import Steps
from app.core.services.users import fetch_user_by_phone, update_user_by_phone


async def fetch_participations(
    limit: Optional[int] = None,
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

    if not user or not user.get("_id"):
        raise ValueError("User is required")

    flow = Steps.ONBOARDING.value if user.get(
        "complete") == False else Steps.NEW_PARTICIPATION.value

    try:
        result = await ParticipationsCollection().insert_one({
            "datetime": datetime.now(),
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
    # Convert ObjectId to string
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

    try:
        participation.serial_number = serial_number
        await ParticipationsCollection().update_one(
            {"_id": id},
            {"$set": {
                "serial_number": serial_number,
            }}
        )
    except Exception as e:
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

    today = datetime.now().strftime("%Y-%m-%d")

    user.submissions[today] = user.submissions.get(today, 0) + 1
    await update_user_by_phone(phone, user)
