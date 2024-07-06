from app.schemas import Participation
from app.utils.decorators import convert_id_to_str


def serialize_participation(participation: Participation):
    return {
        "_id": participation.id,
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
