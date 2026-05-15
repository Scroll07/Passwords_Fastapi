from enum import StrEnum

from pydantic import BaseModel


class TokenType(StrEnum):
    BEARER = "bearer"
    REFRESH = "refresh"

class Token(BaseModel):
    token: str
    token_type: TokenType
