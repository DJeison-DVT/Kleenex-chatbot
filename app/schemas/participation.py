from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime
from bson import ObjectId

from app.schemas.user import User


class PrizeType(str, Enum):
    digital = "digital"
    physical = "physical"


class Products(str, Enum):
    product1 = "product1"
    product2 = "product2"
    product3 = "product3"
    product4 = "product4"
    product5 = "product5"
    product6 = "product6"
    product7 = "product7"
    product8 = "product8"
    product9 = "product9"
    product10 = "product10"


class Status(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    REJECTED = "REJECTED"
    APPROVED = "APPROVED"


class ParticipationCreation(BaseModel):
    user: User


class Participation(BaseModel):
    id: str = Field(..., alias="_id")
    user: User
    ticket_url: Optional[str] = None
    ticket_attempts: int = 0
    participationNumber: int = -1
    products: list[Products] = []
    datetime: datetime
    status: Status = Status.INCOMPLETE
    prizeType: Optional[PrizeType] = None
