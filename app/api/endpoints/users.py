from fastapi import APIRouter, HTTPException, Depends, Response

from app.schemas.user import User, UserCreation
from app.api.deps import get_db
from app.serializers.user import serialize_user, serialize_users

router = APIRouter()


async def get_user_by_phone(id: str, db):
    existing_user = await db.users.find_one({"phone": id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    return existing_user


@router.get("/")
async def fetch_all_users(db=Depends(get_db), response_model=User):
    cursor = db.users.find({})
    users = []
    async for user in cursor:
        users.append(user)
    return serialize_users(users)


@router.post("/", response_model=User)
async def create_user(
    user: UserCreation,
    response: Response,
    db=Depends(get_db)
) -> User:
    phone = user.phone
    terms = user.terms

    if not phone:
        raise HTTPException(status_code=400, detail="Phone number is required")
    try:
        result = await db.users.insert_one({"phone": phone, "terms": terms, "flow_step": "onboarding"})
    except Exception as e:
        if e.code == 11000:
            raise HTTPException(status_code=409, detail="User already exists")
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    new_user = await db.users.find_one({"_id": result.inserted_id})

    response.status_code = 201

    return serialize_user(new_user)


@router.delete("/{phone}")
async def delete_user_by_phone(phone: str, response: Response, db=Depends(get_db)):
    await get_user_by_phone(phone, db)
    await db.users.delete_one({"phone": phone})
    response.status_code = 204
    return {"message": "User deleted successfully"}


@router.get("/{phone}")
async def fetch_user_by_phone(phone: str, db=Depends(get_db), response_model=User):
    user = await get_user_by_phone(phone, db)
    return serialize_user(user)


@router.put("/{phone}")
async def update_user_by_phone(phone: str, user: User, db=Depends(get_db), response_model=User):
    await get_user_by_phone(phone, db)

    old_user = await get_user_by_phone(phone, db)
    id = old_user.get('_id')
    new_user = user.to_dict()
    new_user.pop('_id', None)
    try:
        await db.users.update_one({"_id": id}, {"$set": new_user})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}")

    user = await db.users.find_one({"_id": id})
    return serialize_user(user)
