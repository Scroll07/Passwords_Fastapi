from pydantic import BaseModel
from enum import StrEnum

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

