from app.schemas import Participation
from app.serializers.decorators import convert_id_to_str
from app.serializers.user import serialize_user


@convert_id_to_str(Participation)
def serialize_participation(participation: Participation):
    return {
        "_id": str(participation.id),
        "user": participation.user,
        "ticket_url": participation.ticket_url,
        "ticket_attempts": participation.ticket_attempts,
        "participationNumber": participation.participationNumber,
        "products": participation.products,
        "datetime": participation.datetime,
        "status": participation.status,
        "prizeType": participation.prizeType,
    }


def serialize_participations(participations):
    return [serialize_participation(participation) for participation in participations]
