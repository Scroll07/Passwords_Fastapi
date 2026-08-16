from pydantic import BaseModel

from backend.schemas.jwt import JWTDecodedData
from backend.models.model import Vaults


class RequstVaultDependecie(BaseModel):
    token_data: JWTDecodedData
    vault: Vaults
    # username: str