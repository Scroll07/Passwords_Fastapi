from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class TokenType(StrEnum):
    BEARER = "bearer"
    REFRESH = "refresh"

    
class JWTDecodedData(BaseModel):
    sub: str
    sid: int
    exp: int
    type: TokenType
    

class EncodedToken(BaseModel):
    token: str
    
