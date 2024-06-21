from pydantic import BaseModel
from enum import Enum
from datetime import datetime

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
    phone_number: str
    date: datetime
    status: Status
    photo_url: str
    serial_number: str | None = None
    priority_number: int | None = None
    type: PrizeType | None = None
    products: list[Products] | None = None

