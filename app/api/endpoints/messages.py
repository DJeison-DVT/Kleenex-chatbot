from fastapi import APIRouter, HTTPException, Response, Depends, Query
from typing import Annotated

from app.core.auth import *
from app.chatbot.messages import get_user_messages

router = APIRouter()


@router.get("/history")
async def fetch_user_messages(
    response: Response,
    _: Annotated[DashboardUser, Depends(get_current_user)],
    id: str = Query(..., description="The id of the user")
):
    messages = await get_user_messages(id)
    if not messages:
        raise HTTPException(
            status_code=404, detail="No messages found for this phone number")

    return messages
