import pytest
import random
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

from app.core.services.priority_number import set_priority_number, get_prize
from app.schemas.participation import Participation, Status
from app.schemas.user import User
from app.chatbot.steps import Steps
from app.db.db import _MongoClientSingleton
from app.core.services.datetime_mexico import get_current_datetime


@pytest.mark.asyncio
async def test_get_prize(db: AsyncIOMotorClient, clean_db):
    today = get_current_datetime()
    priority_number = 1
    prize = "Test Prize"
    await db.prizes.insert_one({
        "priority_number": priority_number,
        "date": today,
        "prize": prize,
        "taken": False,
    })

    result = await get_prize(priority_number, today, None)
    assert result == prize

    result = await db.prizes.find_one({"priority_number": priority_number, "date": today})
    assert result["taken"] == True

    result = await get_prize(priority_number + 1, today, None)
    assert result is None

    result = await get_prize(priority_number, today + timedelta(days=1), None)
    assert result is None

    result = await get_prize(priority_number + 1, today + timedelta(days=1), None)
    assert result is None


@pytest.mark.asyncio
async def test_multiple_prizes(db: AsyncIOMotorClient, clean_db):
    today = get_current_datetime()

    prizes = [f"Prize {i}" for i in range(1, 26)]  # 25 prizes
    # Generate 25 unique random numbers from 1 to 100
    priority_numbers = random.sample(range(1, 101), 25)

    # Insert prizes into the database
    for priority_number, prize in zip(priority_numbers, prizes):
        await db.prizes.insert_one({
            "priority_number": priority_number,
            "date": today,
            "prize": prize,
            "taken": False,
        })

    async with await _MongoClientSingleton().mongo_client.start_session() as session:
        async with session.start_transaction():
            # Retrieve and verify prizes
            for priority_number, prize in zip(priority_numbers, prizes):
                result = await get_prize(priority_number, today, session)
                assert result == prize

                result = await db.prizes.find_one({"priority_number": priority_number, "date": today}, session=session)
                assert result["taken"] == True

            # Verify that no additional prizes can be taken for non-existing priority numbers
            all_possible_numbers = set(range(1, 101))
            used_numbers = set(priority_numbers)
            unused_numbers = all_possible_numbers - used_numbers

            for priority_number in unused_numbers:
                result = await get_prize(priority_number, today, session)
                assert result is None

            # Verify that no prizes can be taken for a different day
            for priority_number in priority_numbers:
                result = await get_prize(priority_number, today + timedelta(days=1), session)
                assert result is None


@pytest.mark.asyncio
async def test_set_priority_number(db: AsyncIOMotorClient, clean_db):
    # Create a user
    user_data = {
        "name": "Test User",
        "email": "dijfseiajfo@example.com",
        "phone": "1234567890",
        "terms": True,
        "complete": True
    }

    inserted_user = await db.users.insert_one(user_data)

    # Fetch the user back from the database
    result = await db.users.find_one({"_id": inserted_user.inserted_id})
    result['_id'] = str(result['_id'])
    user = User(**result)

    # Create a participation
    participation_data = {
        "user": user.to_dict(),
        "datetime": get_current_datetime(),
        "status": Status.INCOMPLETE.value,
        "flow": Steps.PRIORITY_NUMBER.value,
    }
    inserted_participation = await db.participations.insert_one(participation_data)

    # Fetch the participation back from the database
    result = await db.participations.find_one({"_id": inserted_participation.inserted_id})
    result['_id'] = str(result['_id'])
    participation = Participation(**result)

    # Set the priority number for the participation
    priority_assigned = await set_priority_number(participation)

    # Fetch the updated participation
    updated_participation = await db.participations.find_one({"_id": inserted_participation.inserted_id})
    updated_participation['_id'] = str(updated_participation['_id'])
    participation = Participation(**updated_participation)

    # Assert that the priority number is assigned and is 1
    assert participation.priority_number == 1
    assert participation.status == Status.COMPLETE.value

    # Fetch the counter for today
    counter_result = await db.counters.find_one({"_id": get_current_datetime().strftime("%Y-%m-%d")})
    assert counter_result is not None
    assert counter_result["value"] == 1

    # Ensure the result of the set_priority_number function call
    assert priority_assigned is False


@ pytest.mark.asyncio
async def test_set_priority_numbers(db: AsyncIOMotorClient, clean_db):
    user_data = {
        "name": "Test User",
        "email": "dijfseiajfo@example.com",
        "phone": "1234567890",
        "terms": True,
        "complete": True
    }

    inserted_user = await db.users.insert_one(user_data)

    result = await db.users.find_one({"_id": inserted_user.inserted_id})
    result['_id'] = str(result['_id'])
    user = User(**result)

    sample_participations = []
    for _ in range(5):
        participation_data = {
            "user": user.to_dict(),
            "datetime": get_current_datetime(),
            "status": Status.INCOMPLETE.value,
            "flow": Steps.PRIORITY_NUMBER.value,
        }

        created_result = await db.participations.insert_one(participation_data)
        result = await db.participations.find_one({"_id": created_result.inserted_id})
        result['_id'] = str(result['_id'])
        participation = Participation(**result)

        has_prize = await set_priority_number(participation)
        assert has_prize is False

        result = await db.participations.find_one({"_id": created_result.inserted_id})
        result['_id'] = str(result['_id'])
        sample_participations.append(Participation(**result))

    for idx, participation in enumerate(sample_participations):
        assert participation.priority_number == idx + 1
        assert participation.status == Status.COMPLETE.value
        assert participation.prize is None

    # Verify that the priority numbers are unique
    priority_numbers = [
        participation.priority_number for participation in sample_participations]

    assert len(priority_numbers) == len(set(priority_numbers))
