from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user import User, UserCreation
from pydantic import EmailStr
from app.api.deps import get_db
from app.serializers.user import serialize_user, serialize_users, serialize_user_dict

router = APIRouter()

@router.get("/")
async def fetch_all_users(db = Depends(get_db), response_model=User):
    cursor = db.users.find({})
    users = []
    async for user in cursor:
        users.append(serialize_user_dict(user))
    return serialize_users(users)

@router.post("/", response_model=User)
async def create_user(
    user: UserCreation,
    db = Depends(get_db)
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

    return serialize_user(serialize_user_dict(new_user))

@router.delete("/{phone}")
async def delete_user_by_phone(phone: str, db = Depends(get_db)):
    user = await db.users.find_one({"phone": phone})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.users.delete_one({"phone": phone})
    return {"message": "User deleted successfully"}

@router.get("/{phone}")
async def fetch_user_by_phone(phone: str, db = Depends(get_db), response_model=User):
    user = await db.users.find_one({"phone": phone})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_user(serialize_user_dict(user))

@router.put("/{phone}")
async def update_user_by_phone(phone: str, user: User, db = Depends(get_db), response_model=User):
    old_user = await db.users.find_one({"phone": phone})
    if not old_user:
        raise HTTPException(status_code=404, detail="User not found")
                    
    id = old_user.get('_id')
    try:
        await db.users.update_one({"_id": id}, {"$set": {
            "phone": user.phone,
            "terms": user.terms,
            "name": user.name,
            "email": user.email,
            "flow_step": user.flow_step
        }})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    
    user = await db.users.find_one({"_id": id})
    return serialize_user(serialize_user_dict(user))