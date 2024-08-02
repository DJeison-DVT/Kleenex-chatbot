from typing import Dict
from datetime import datetime

from app.core.auth import DashboardUserInDB, DashboardUser
from app.db.db import ParticipationLogs


async def save_participation_log(ticket_id, current_user: DashboardUserInDB, info: Dict):
    current_user = DashboardUser(
        username=current_user.username,
        role=current_user.role
    )

    log_entry = {
        "ticket_id": ticket_id,
        "dashboard_user": current_user.model_dump(),
        "info": info,
        "timestamp": datetime.now()
    }

    result = await ParticipationLogs().insert_one(log_entry)
    return result
