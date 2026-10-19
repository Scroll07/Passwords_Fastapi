




from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field


class VaultData(BaseModel):
    id: int
    name: str
    entries: int
    pinned: bool
    version: int
    
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def created_at_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        
    model_config = ConfigDict(from_attributes=True)
    
class EncryptedUserVault(BaseModel):
    name: str
    salt: str
    encrypted_dek: str
    encrypted_passwords: str
    version: int
    
    model_config = ConfigDict(from_attributes=True)

class VaultPushDataRequest(BaseModel):
    name: str
    encrypted_passwords: str
    entries: int
    version: int