from typing import List
from functools import wraps

from app.schemas import User


def convert_id_to_str(func):
    @wraps(func)
    def wrapper(user_dict):
        if '_id' in user_dict:
            user_dict['_id'] = str(user_dict['_id'])
            user = User(**user_dict)
        return func(user)
    return wrapper


@convert_id_to_str
def serialize_user(user: User):
    return {
        "_id": str(user.id),
        "phone": user.phone,
        "terms": user.terms,
        "name": user.name if user.name else None,
        "email": user.email if user.email else None,
        "flow_step": user.flow_step,
    }


def serialize_users(users: List[User]):
    return [serialize_user(user) for user in users]
