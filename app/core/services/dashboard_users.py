from typing import List

from app.schemas.auth import DisplayDashboardUser
from app.db.db import DashboardUsers


async def fetch_dashboard_users() -> List[DisplayDashboardUser]:
    cursor = DashboardUsers().find()
    users = []
    async for user in cursor:
        user['_id'] = str(user['_id'])
        users.append(DisplayDashboardUser(**user))
    return users
