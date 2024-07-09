import pytest
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

from app.schemas.participation import ParticipationCreation, Participation, Status
from app.schemas.user import User
from app.core.services.participations import *


@pytest.mark.asyncio
async def test_create_participation(db: AsyncIOMotorClient, clean_db):
    user_data = {
        "_id": "user1",
        "phone": "1234567891",
        "terms": True,
        "name": "Test User",
        "email": "test1@example.com",
        "status": "INCOMPLETE",
        "submissions": {}
    }
    user = User(**user_data)
    participation_data = ParticipationCreation(user=user)

    participation = await create_participation(participation_data)

    assert participation.user.phone == "1234567891"
    assert participation.status == Status.INCOMPLETE.value
    assert participation.flow == Steps.ONBOARDING.value
    assert isinstance(participation.id, str)  # Ensure _id is a string

    count = await db.participations.count_documents({})
    assert count == 1


@pytest.mark.asyncio
async def test_fetch_participations(db: AsyncIOMotorClient, clean_db):
    user_data = {
        "_id": "user2",
        "phone": "1234567892",
        "terms": True,
        "name": "Test User",
        "email": "test2@example.com",
        "status": "INCOMPLETE",
        "submissions": {}
    }
    participation_data = {
        "datetime": datetime.now(),
        "user": user_data,
        "status": Status.INCOMPLETE.value
    }
    await db.participations.insert_one(participation_data)

    participations = await fetch_participations()

    assert len(participations) == 1
    assert participations[0].user.phone == "1234567892"


@pytest.mark.asyncio
async def test_fetch_participation_by_id(db: AsyncIOMotorClient, clean_db):
    user_data = {
        "_id": "user3",
        "phone": "1234567893",
        "terms": True,
        "name": "Test User",
        "email": "test3@example.com",
        "status": "INCOMPLETE",
        "submissions": {}
    }
    participation_data = {
        "_id": ObjectId(),
        "datetime": datetime.now(),
        "user": user_data,
        "status": Status.INCOMPLETE.value
    }
    result = await db.participations.insert_one(participation_data)

    participation = await fetch_participation_by_id(str(result.inserted_id))

    assert participation.user.phone == "1234567893"


@pytest.mark.asyncio
async def test_fetch_participation_by_phone(db: AsyncIOMotorClient, clean_db):
    user_data = {
        "_id": "user4",
        "phone": "1234567894",
        "terms": True,
        "name": "Test User",
        "email": "test4@example.com",
        "status": "INCOMPLETE",
        "submissions": {}
    }
    participation_data = {
        "datetime": datetime.now(),
        "user": user_data,
        "status": Status.INCOMPLETE.value
    }
    await db.participations.insert_one(participation_data)

    participation = await fetch_participation_by_phone("1234567894")

    assert participation.user.phone == "1234567894"


@pytest.mark.asyncio
async def test_count_participations(db: AsyncIOMotorClient, clean_db):
    user_data = {
        "_id": "user5",
        "phone": "1234567895",
        "terms": True,
        "name": "Test User",
        "email": "test5@example.com",
        "status": "INCOMPLETE",
        "submissions": {}
    }
    participation_data = {
        "datetime": datetime.now(),
        "user": user_data,
        "status": Status.COMPLETE.value
    }

    await db.participations.insert_one(participation_data)

    participation_data = {
        "datetime": datetime.now(),
        "user": user_data,
        "status": Status.INCOMPLETE.value
    }

    await db.participations.insert_one(participation_data)

    count = await count_participations()

    assert count == 1


@pytest.mark.asyncio
async def test_update_participation(db: AsyncIOMotorClient, clean_db):
    user_data = {
        "_id": "user6",
        "phone": "1234567896",
        "terms": True,
        "name": "Test User",
        "email": "test6@example.com",
        "status": "INCOMPLETE",
        "submissions": {}
    }
    participation_data = {
        "_id": ObjectId(),
        "datetime": datetime.now(),
        "user": user_data,
        "status": Status.INCOMPLETE.value,
        "flow": Steps.ONBOARDING.value
    }
    result = await db.participations.insert_one(participation_data)

    participation_data["_id"] = str(result.inserted_id)
    participation_update = Participation(**participation_data)
    participation_update.status = Status.COMPLETE

    updated_participation = await update_participation(str(result.inserted_id), participation_update)

    assert updated_participation.status == Status.COMPLETE


@pytest.mark.asyncio
async def test_delete_participation_by_id(db: AsyncIOMotorClient, clean_db):
    user_data = {
        "_id": "user7",
        "phone": "1234567897",
        "terms": True,
        "name": "Test User",
        "email": "test7@example.com",
        "status": "INCOMPLETE",
        "submissions": {}
    }
    participation_data = {
        "_id": ObjectId(),
        "datetime": datetime.now(),
        "user": user_data,
        "status": Status.INCOMPLETE.value
    }
    result = await db.participations.insert_one(participation_data)

    await delete_participation_by_id(str(result.inserted_id))

    deleted_participation = await db.participations.find_one({"_id": result.inserted_id})
    assert deleted_participation is None
