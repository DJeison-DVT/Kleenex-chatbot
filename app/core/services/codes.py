from bson import ObjectId
from fastapi import HTTPException

from app.schemas.participation import Participation
from app.schemas.prize import Code
from app.db.db import PrizeCodesCollection


async def get_code_by_participation(participation: Participation):
    id = ObjectId(participation.id)
    assigned_code = await PrizeCodesCollection().find_one({"participationId": id})
    if not assigned_code:
        raise HTTPException(status_code=404, detail="No available code found")

    assigned_code["_id"] = str(assigned_code["_id"])
    assigned_code["participationId"] = str(assigned_code["participationId"])
    return Code(**assigned_code)
