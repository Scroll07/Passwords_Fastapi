from pydantic import BaseModel

from backend.schemas.db_schema import SessionType

    
class JWTDecodedData(BaseModel):
    sub: str
    sid: int
    exp: int
    type: SessionType
    
class VaultDecodedData(JWTDecodedData):
    encrypted_dek: str

class EncodedToken(BaseModel):
    token: str
    
