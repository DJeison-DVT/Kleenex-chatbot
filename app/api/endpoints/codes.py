from fastapi import APIRouter, HTTPException, Response

from app.core.services.codes import code_counts

router = APIRouter()


@router.get("/count")
async def get_code_counters():
    code_counters = await code_counts()
    return code_counters
