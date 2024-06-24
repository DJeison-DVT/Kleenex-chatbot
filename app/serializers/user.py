from typing import List

from app.schemas import User
from app.serializers.decorators import convert_id_to_str


@convert_id_to_str(User)
def serialize_user(user: User):
    return {
        "_id": str(user.id),
        "phone": user.phone,
        "terms": user.terms,
        "name": user.name if user.name else None,
        "email": user.email if user.email else None,
        "flow_step": user.flow_step,
        "submissions": user.submissions if user.submissions else {},
    }


def serialize_users(users: List[User]):
    return [serialize_user(user) for user in users]
