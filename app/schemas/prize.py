from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from bson import ObjectId


class Code(BaseModel):
    id: str = Field(..., alias="_id")
    participationId: str = None
    amount: int
    link: HttpUrl
    code: str
    taken: bool
