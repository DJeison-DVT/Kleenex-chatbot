from fastapi import APIRouter, HTTPException, Response, Depends
from pydantic import BaseModel
from typing import Annotated

from app.core.auth import RoleChecker, get_current_user, DashboardUserInDB, DashboardUser
from app.core.services.participations import accept_participation, fetch_participation_by_id, update_participation
from app.core.services.dashboard_users import fetch_dashboard_users, delete_dashboard_user_by_id
from app.core.services.logs import save_participation_log
from app.schemas.participation import Status
from app.chatbot.flow import FLOW
from app.chatbot.user_flow import FlowManager

router = APIRouter()


class AcceptRequest(BaseModel):
    ticket_id: str
    serial_number: str | None = None
    rejection_reason: str | None = None


async def handle_accept(ticket_id, current_user: DashboardUserInDB, serial_number=None, rejection_reason=None):
    try:
        participation = await fetch_participation_by_id(ticket_id)
        user = participation.user
        if participation.status != Status.COMPLETE.value:
            raise ValueError("Participation cannot be accepted")
        result = await accept_participation(participation, serial_number)
        if rejection_reason:
            participation.rejection_reason = rejection_reason
            await update_participation(participation.id, participation)
            await save_participation_log(ticket_id, current_user, {'interaction_type': 'rejected'})
        else:
            await save_participation_log(ticket_id, current_user, {'interaction_type': 'accepted'})

        flow_manager = FlowManager(FLOW, user, participation)
        await flow_manager.execute(response=result)
    except Exception as e:
        raise e


@router.post("/accept")
async def accept(
    request: AcceptRequest,
    response: Response,
    current_user: Annotated[DashboardUser, Depends(get_current_user)],
):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"

    try:
        ticket_id = request.ticket_id
        serial_number = request.serial_number
        return await handle_accept(ticket_id, current_user, serial_number=serial_number)
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


@router.post("/reject")
async def reject(
    request: AcceptRequest,
    response: Response,
    current_user: Annotated[DashboardUser, Depends(get_current_user)],
):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"

    try:
        ticket_id = request.ticket_id
        reason = request.rejection_reason
        return await handle_accept(ticket_id, current_user, rejection_reason=reason)
    except Exception as e:
        print(e)
        response.status_code = 500
        return HTTPException(status_code=500, detail=f"Internal server error : {e}")


@router.get("/users")
async def get_dashboard_users(
        _: Annotated[bool, Depends(RoleChecker(allowed_roles=["admin"]))]
):
    return await fetch_dashboard_users()


class DeleteUserRequest(BaseModel):
    user_id: str


@router.delete("/users")
async def delete_dashboard_user(
    request: DeleteUserRequest, response: Response,
    _: Annotated[bool, Depends(RoleChecker(allowed_roles=["admin"]))]
):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    try:
        user_id = request.user_id
        await delete_dashboard_user_by_id(user_id)
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    response.status_code = 204
    return {"message": "User deleted successfully"}
