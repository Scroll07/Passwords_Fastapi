from pydantic import BaseModel, ConfigDict

from backend.schemas.jwt import JWTDecodedData
from backend.models.model import Vaults


class RequstVaultDependecie(BaseModel):
    # token_data: JWTDecodedData
    vault: Vaults
    master_password: str
    # username: str
    
    model_config = ConfigDict(arbitrary_types_allowed=True)