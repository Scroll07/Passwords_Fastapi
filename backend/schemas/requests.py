from pydantic import BaseModel, ConfigDict

from backend.models.model import Vaults


class RequstVaultDependecie(BaseModel):
    vault: Vaults
    dek: bytes
    
    model_config = ConfigDict(arbitrary_types_allowed=True)