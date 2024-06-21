from typing import List
from app.schemas import User

def serialize_user(user: User):
    return {
        "phone": user.phone,
        "terms": user.terms,
        "name": user.name if user.name else None,
        "email": user.email if user.email else None,
        "flow_step": user.flow_step
    }

def serialize_users(users: List[User]):
    return [serialize_user(user) for user in users]