from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from bson import ObjectId

from app.schemas.user import User


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v)


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


class Participation(BaseModel):
    id: str = Field(..., alias="_id")
    user: User
    ticket_url: str | None = None
    ticket_attempts: int = 0
    participationNumber: int = -1
    products: list[Products] = []
    datetime: datetime
    status: Status = Status.INCOMPLETE
    prizeType: PrizeType | None = None
