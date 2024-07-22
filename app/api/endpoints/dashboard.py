from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

from app.core.services.participations import accept_participation, fetch_participation_by_id
from app.schemas.participation import Status
from app.chatbot.flow import FLOW
from app.chatbot.user_flow import FlowManager

router = APIRouter()


class AcceptRequest(BaseModel):
    ticket_id: str
    serial_number: str | None = None


async def handle_accept(ticket_id, serial_number):
    try:
        participation = await fetch_participation_by_id(ticket_id)
        user = participation.user
        if participation.status != Status.COMPLETE.value:
            raise ValueError("Participation cannot be accepted")
        result = await accept_participation(participation, serial_number)
        flow_manager = FlowManager(FLOW, user, participation)
        await flow_manager.execute(response=result)
    except Exception as e:
        raise e


@router.post("/accept")
async def accept(request: AcceptRequest, response: Response):
    try:
        ticket_id = request.ticket_id
        serial_number = request.serial_number
        return await handle_accept(ticket_id, serial_number)
    except Exception as e:
        if str(e) in ["Serial number already set", "Duplicate Serial Number"]:
            response.status_code = 409
            return HTTPException(status_code=409, detail=str(e))
        elif str(e) in ["Participation cannot be accepted"]:
            response.status_code = 400
            return HTTPException(status_code=400, detail=str(e))
        print(e)

        response.status_code = 500
        return HTTPException(status_code=500, detail="Internal server error")
