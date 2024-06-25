from fastapi import APIRouter, Depends, Response, HTTPException
from pymongo.errors import InvalidDocument
from datetime import datetime
from bson import ObjectId

from app.schemas.participation import Participation, ParticipationCreation
from app.api.deps import get_db
from app.serializers.participation import serialize_participations, serialize_participation

router = APIRouter()


async def get_participation_by_id(id: str, db):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    id = ObjectId(id)
    existing_participation = await db.participations.find_one({"_id": id})
    if not existing_participation:
        raise HTTPException(status_code=404, detail="Participation not found")

    return existing_participation


@router.get("/")
async def fetch_all_participations(db=Depends(get_db), response_model=Participation):
    cursor = db.participations.find({})
    participations = []
    async for participation in cursor:
        participations.append(participation)
    return serialize_participations(participations)


@router.get("/{id}")
async def fetch_participation_by_id(id: str, db=Depends(get_db), response_model=Participation):
    participation = await get_participation_by_id(id, db)
    return serialize_participation(participation)


@router.post("/", response_model=Participation)
async def create_participation(
    participation: ParticipationCreation,
    response: Response,
    db=Depends(get_db)
) -> Participation:
    user = participation.user.to_dict()

    if not user:
        raise HTTPException(
            status_code=400, detail="User is required")
    try:
        result = await db.participations.insert_one({"user": user, "datetime": datetime.now()})
    except InvalidDocument as e:
        raise HTTPException(
            status_code=400, detail="Invalid participation data")
    except Exception as e:
        if hasattr(e, 'code') and e.code == 11000:
            raise HTTPException(
                status_code=409, detail="Participation already exists")
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    new_participation = await db.participations.find_one({"_id": result.inserted_id})

    response.status_code = 201

    return serialize_participation(new_participation)


@router.put("/{id}")
async def update_participation_by_id(
    id: str,
    participation: Participation,
    response: Response,
    db=Depends(get_db)
):
    await get_participation_by_id(id, db)
    id = ObjectId(id)
    new_participation = participation.to_dict()
    new_participation.pop("_id", None)

    try:
        await db.participations.update_one({"_id": id}, {"$set": new_participation})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

    participation = await db.participations.find_one({"_id": id})
    return serialize_participation(participation)


@router.delete("/{id}")
async def delete_participation_by_id(id: str, response: Response, db=Depends(get_db)):
    await get_participation_by_id(id, db)
    id = ObjectId(id)
    await db.participations.delete_one({"_id": id})
    response.status_code = 204
    return {"message": "Participation deleted successfully"}
