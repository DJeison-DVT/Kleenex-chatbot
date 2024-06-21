from typing import List
from app.schemas import User

def serialize_user(user: User):
    print(f"user: {user}")
    return {
        "phone": user.phone,
        "terms": user.terms,
        "name": user.name,
        "email": user.email,
        "flow_step": user.flow_step
    }

def serialize_users(users: List[User]):
    return [serialize_user(user) for user in users]