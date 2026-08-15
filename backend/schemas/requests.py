from pydantic import BaseModel

from backend.schemas.jwt import JWTDecodedData



class RequstVaultDependecie(BaseModel):
    token_data: JWTDecodedData
    vault_name: str
    username: str