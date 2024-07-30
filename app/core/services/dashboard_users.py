from typing import List
from bson import ObjectId

from app.schemas.auth import DisplayDashboardUser
from app.db.db import DashboardUsers


async def fetch_dashboard_users() -> List[DisplayDashboardUser]:
    cursor = DashboardUsers().find()
    users = []
    async for user in cursor:
        user['_id'] = str(user['_id'])
        users.append(DisplayDashboardUser(**user))
    return users


async def delete_dashboard_user_by_id(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid ID")
    object_id = ObjectId(user_id)
    result = await DashboardUsers().delete_one({"_id": object_id})
    if not result.deleted_count > 0:
        raise ValueError('not found')
