from fastapi import APIRouter, Depends, Response, HTTPException

from app.schemas.participation import Participation
from app.api.deps import get_db
from app.serializers.participation import serialize_participations, serialize_participation

router = APIRouter()


@router.get("/")
async def fetch_all_participations(db=Depends(get_db), response_model=Participation):
    cursor = db.participations.find({})
    participations = []
    async for participation in cursor:
        participations.append(participation)
    return serialize_participations(participations)
