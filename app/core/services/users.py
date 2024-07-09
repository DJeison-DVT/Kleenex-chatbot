from typing import List

from app.schemas.user import User, UserCreation
from app.db.db import UsersCollection, ParticipationsCollection, _MongoClientSingleton


async def fetch_users() -> List[User]:
    cursor = UsersCollection().find()
    users = []
    async for user in cursor:
        user["_id"] = str(user["_id"])
        users.append(User(**user))
    return users


async def fetch_user_by_phone(phone: str) -> User:
    existing_user = await UsersCollection().find_one({"phone": phone})
    if not existing_user:
        raise ValueError("User not found")
    existing_user["_id"] = str(existing_user["_id"])
    return User(**existing_user)


async def create_user(user: UserCreation) -> User:
    phone = user.phone

    if not phone:
        raise ValueError("Phone number is required")

    try:
        result = await UsersCollection().insert_one({"phone": phone, "terms": False, "complete": False})
    except AttributeError as e:
        raise ValueError(f"Error: {e}")
    except Exception as e:
        if e.code == 11000:
            raise ValueError("User already exists")
        raise ValueError(f"Error: {e}")
    new_user = await UsersCollection().find_one({"_id": result.inserted_id})

    new_user["_id"] = str(new_user["_id"])
    return User(**new_user)


async def update_user_by_phone(phone: str, user: User) -> User:
    old_user = await UsersCollection().find_one({"phone": phone})
    id = old_user.get("_id")

    new_user = user.to_dict()
    new_user.pop("_id", None)

    try:
        async with await _MongoClientSingleton().mongo_client.start_session() as session:
            async with session.start_transaction():
                await UsersCollection().update_one({"_id": id}, {"$set": new_user}, session=session)

                await ParticipationsCollection().update_many(
                    {"user.phone": user.phone},
                    {"$set": {"user": new_user}},
                    session=session
                )
    except Exception as e:
        raise ValueError(f"Error: {e}")

    updated_user = await UsersCollection().find_one({"_id": id})
    updated_user["_id"] = str(updated_user["_id"])
    return User(**updated_user)


async def delete_user_by_phone(phone: str):
    user = await UsersCollection().find_one({"phone": phone})
    if not user:
        raise ValueError("User not found")

    await UsersCollection().delete_one({"phone": phone})
