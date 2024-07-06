from fastapi import APIRouter, HTTPException, Depends, Response
from pymongo.errors import InvalidDocument

from app.schemas.user import User, UserCreation
from app.api.deps import get_db
from app.utils.decorators import check_existence
from app.core.services.users import *
from app.serializers.user import serialize_user, serialize_users

router = APIRouter()


@check_existence
async def get_user_by_phone(phone: str):
    user = await fetch_user_by_phone(phone)
    return serialize_user(user)


@check_existence
async def get_users():
    users = await fetch_users()
    return serialize_users(users)


@router.get("/")
async def fetch_all_users(response_model=User):
    return await get_users()


@router.post("/", response_model=User)
async def api_create_user(
    user: UserCreation,
    response: Response,
) -> User:
    try:
        new_user = await create_user(user)
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=f"Error: {e}")
    except InvalidDocument as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Error: {e}")
    except Exception as e:
        if "duplicate phone" in str(e):
            raise HTTPException(status_code=409, detail="User already exists")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

    response.status_code = 201
    return serialize_user(new_user)


@router.delete("/{phone}")
async def api_delete_user_by_phone(phone: str, response: Response):
    try:
        await get_user_by_phone(phone)
        await delete_user_by_phone(phone)
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    response.status_code = 204
    return {"message": "User deleted successfully"}


@router.get("/{phone}")
async def api_fetch_user_by_phone(phone: str, response_model=User):
    return await get_user_by_phone(phone)


@router.put("/{phone}")
async def put_user_by_phone(phone: str, user: User, response_model=User):
    try:
        await get_user_by_phone(phone)
        updated_user = await update_user_by_phone(phone, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    return serialize_user(updated_user)
