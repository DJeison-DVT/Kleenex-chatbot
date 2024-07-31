from fastapi import APIRouter, HTTPException, Response, Query

from app.chatbot.messages import get_user_messages

router = APIRouter()


@router.get("/")
async def fetch_user_messages(response: Response, id: str = Query(..., description="The phone number of the user")):
    messages = await get_user_messages(id)
    if not messages:
        raise HTTPException(
            status_code=404, detail="No messages found for this phone number")

    return messages
