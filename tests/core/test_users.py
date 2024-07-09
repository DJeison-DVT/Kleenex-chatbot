import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.services.users import *
from app.schemas.user import User, UserCreation


@pytest.mark.asyncio
async def test_create_user(db: AsyncIOMotorClient, clean_db):
    user_data = UserCreation(phone="1234567890")
    user = await create_user(user_data)

    assert user.phone == "1234567890"
    assert user.terms is False
    assert user.complete is False


@pytest.mark.asyncio
async def test_fetch_users(db: AsyncIOMotorClient, clean_db):
    user_data1 = {"phone": "1234567891",
                  "terms": True, "complete": False}
    user_data2 = {"phone": "1234567892",
                  "terms": False, "complete": True}

    await db.users.insert_many([user_data1, user_data2])

    users = await fetch_users()

    assert len(users) == 2
    assert users[0].phone in ["1234567891", "1234567892"]
    assert users[1].phone in ["1234567891", "1234567892"]


@pytest.mark.asyncio
async def test_fetch_user_by_phone(db: AsyncIOMotorClient, clean_db):
    user_data = {"phone": "1234567893",
                 "terms": True, "complete": False}
    await db.users.insert_one(user_data)

    user = await fetch_user_by_phone("1234567893")

    assert user.phone == "1234567893"
    assert user.terms is True
    assert user.complete == False


@pytest.mark.asyncio
async def test_update_user_by_phone(db: AsyncIOMotorClient, clean_db):
    user_data = {"phone": "1234567894",
                 "terms": False, "complete": False}
    await db.users.insert_one(user_data)

    user = await fetch_user_by_phone("1234567894")
    user.terms = True
    user.complete = True

    updated_user = await update_user_by_phone("1234567894", user)

    assert updated_user.phone == "1234567894"
    assert updated_user.terms is True
    assert updated_user.complete == True


@pytest.mark.asyncio
async def test_delete_user_by_phone(db: AsyncIOMotorClient, clean_db):
    user_data = {"phone": "1234567895",
                 "terms": True, "complete": False}
    await db.users.insert_one(user_data)

    await delete_user_by_phone("1234567895")

    with pytest.raises(ValueError, match="User not found"):
        await fetch_user_by_phone("1234567895")
