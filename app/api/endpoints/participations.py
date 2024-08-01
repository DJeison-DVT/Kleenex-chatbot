from fastapi import APIRouter, Response, HTTPException, Query
from typing import Optional, Annotated
from pymongo.errors import InvalidDocument
from datetime import datetime


from app.core.auth import *
from app.utils.decorators import check_existence, validate_object_id
from app.schemas.participation import Participation, ParticipationCreation
from app.serializers.participation import serialize_participations, serialize_participation
from app.core.services.participations import *
from app.core.services.priority_number import count_participations
from app.core.services.datetime_mexico import *

router = APIRouter()


@check_existence
@validate_object_id
async def get_participation_by_id(id: str):
    participation = await fetch_participation_by_id(id)
    return serialize_participation(participation)


@check_existence
async def get_participations(limit: int, date: datetime, phone: str, status: str):
    try:
        participations = await fetch_participations(limit, date, phone, status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    return serialize_participations(participations)


@check_existence
async def get_participation_by_phone(phone: str):
    participation = await fetch_participation_by_phone(phone)
    return serialize_participation(participation)


@router.get("/")
@check_existence
async def fetch_all_participations(
    _: Annotated[DashboardUser, Depends(get_current_user)],
    limit: Optional[int] = Query(
        None, description="Limit the number of participations returned"),
    date: Optional[datetime] = Query(
        None, description="Filter participations by date"),
    phone: Optional[str] = Query(
        None, description="Filter participations by phone number"),
    status: Optional[str] = Query(
        None, description="Filter participations by status"),
    response_model=Participation
):
    return await get_participations(limit, date, phone, status)


@router.get("/count")
async def api_count_participations(
    date: Optional[datetime] = Query(
        get_current_datetime(), description="Filter participations by date"),
):
    count = await count_participations(date)
    return {"count": count}


@router.get("/{id}")
async def api_fetch_participation_by_id(id: str, response_model=Participation):
    return await get_participation_by_id(id)


@router.post("/", response_model=Participation)
async def post_participation(
    participation: ParticipationCreation,
    response: Response,
) -> Participation:
    try:
        new_participation = await create_participation(participation)
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=f"Error: {e}")
    except InvalidDocument as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")
    except Exception as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=409, detail="Participation already exists")
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {e}")

    response.status_code = 201
    return serialize_participation(new_participation)


@router.put("/{id}")
async def put_participation_by_id(
    id: str,
    participation: Participation,
):
    try:
        # Ensure participation exists
        await get_participation_by_id(id)
        updated_participation = await update_participation(id, participation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    return serialize_participation(updated_participation)


@router.delete("/{id}")
async def api_delete_participation_by_id(id: str, response: Response):
    try:
        # Ensure participation exists
        await get_participation_by_id(id)
        await delete_participation_by_id(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    response.status_code = 204
    return {"message": "Participation deleted successfully"}
