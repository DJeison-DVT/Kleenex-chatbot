from app.schemas import Participation
from app.utils.decorators import convert_id_to_str


def serialize_participation(participation: Participation):
    return {
        "_id": participation.id,
        "user": participation.user.to_dict(),
        "ticket_url": participation.ticket_url,
        "ticket_attempts": participation.ticket_attempts,
        "priority_number": participation.priority_number,
        "datetime": participation.datetime,
        "status": participation.status,
        "prize": participation.prize,
        "flow": participation.flow,
        "serial_number": participation.serial_number,
        "rejection_reason": participation.rejection_reason,
    }


def serialize_participations(participations):
    return [serialize_participation(participation) for participation in participations]
