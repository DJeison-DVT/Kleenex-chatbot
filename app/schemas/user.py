from pydantic import BaseModel, Field
from typing import Dict, Optional


class UserCreation(BaseModel):
    phone: str


class User(BaseModel):
    id: str = Field(..., alias="_id")
    phone: str
    terms: Optional[bool] = False
    name: Optional[str] = None
    email: Optional[str] = None
    complete: bool = False
    submissions: Dict[str, int] = Field(default_factory=dict)

    def to_dict(self):
        return {
            "_id": self.id,
            "phone": self.phone,
            "terms": self.terms,
            "name": self.name,
            "email": self.email,
            "complete": self.complete,
            "submissions": {str(k): v for k, v in self.submissions.items()}
        }
