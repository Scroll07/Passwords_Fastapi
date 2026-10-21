from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.models.model import Vaults
from backend.schemas.jwt import EncodedToken
from backend.schemas.db_schema import BackupStats
from backend.schemas.vaults import EncryptedUserVault

# ===================================
#               Types
# ===================================
class RedirectPaths(StrEnum):
    DASHBOARD = "dashboard"
    
    
class TypeResponses(StrEnum):
    MESSAGE = "message"
    LOGIN = "login"
    BACKUPS = "backups"
    DOWNLOAD = "download"
    REFRESH = "refresh"
    STATS = "stats"

class SortByBackups(StrEnum):
    NAME = "name"
    ROWS = "rows"
    CREATED_AT = "created_at"
    
class SortByVaults(StrEnum):
    NAME = "name"
    ENTRIES = "entries"
    CREATED_AT = "created_at"
    
class PushStatuses(StrEnum):
    PUSHED = 'pushed'
    UP_TO_DATE = 'up_to_date'
    OUTDATED = 'outdated'
    OVERWRITTEN = 'overwritten'
    NOT_FOUND = 'not_found'
    
class PullStatuses(StrEnum):
    PULLED = 'pulled'
    UP_TO_DATE = 'up_to_date'
    LOCAL_AHEAD = 'local_ahead'
    NOT_FOUND = 'not_found'

class UserData(BaseModel):
    username: str
    password_hash: str
    telegram_id: int | None
    
# ===================================
#               Requests
# ===================================
class DownloadRequest(BaseModel):
    backup_id: int
    
class DeleteRequest(BaseModel):
    backup_id: int

class UploadRequest(BaseModel):
    name: str = Field(max_length=24)
    rows_count: int

class LoginRequest(BaseModel):
    username: str = Field(min_length=4, max_length=32)
    password: str = Field(min_length=4, max_length=32)
    
    @field_validator("username")
    def validate_username(cls, value: str) -> str:
        if " " in value:
            raise ValueError("Username should be without spaces")
        return value

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if " " in value:
            raise ValueError("Password should be without spaces")
        return value

class RegisterRequestData(LoginRequest):
    # username: str = Field(min_length=4, max_length=32)
    # password: str = Field(min_length=4, max_length=32)
    telegram_id: int | None = Field(default=None)

    @field_validator("telegram_id")
    def validate_telegram_id(cls, value: int) -> int:
        if not (6 < len(str(value)) < 16):
            raise ValueError("Wrong telegram id")
        return value

class CreateVaultDataRequest(BaseModel):
    name: str
    salt: str
    encrypted_dek: str

    @field_validator('name')
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not (1 < len(value) < 32):
            raise ValueError("Wrong length of vault name")
        return value
    
class PullRequestData(BaseModel):
    vault_id: int
    version: int | None
    force: bool

class VaultPushDataRequest(BaseModel):
    id: int | None
    name: str
    salt: str
    entries: int
    encrypted_dek: str
    encrypted_passwords: str
    version: int
    force: bool
# ===================================
#               Responses
# ===================================
class MessageResponse(BaseModel):
    ok: bool
    detail: str

class CreateVaultResponse(MessageResponse):
    vault_id: int

class LoginResponse(MessageResponse):
    bearer_token: EncodedToken
    refresh_token: EncodedToken
    type: TypeResponses = TypeResponses.LOGIN

class RefreshResponse(LoginResponse):
    type: TypeResponses = TypeResponses.REFRESH

    
class BackupStatsResponse(BaseModel):
    ok: bool
    stats: BackupStats
    type: TypeResponses = TypeResponses.STATS
    
    
class UnlockVault(BaseModel):
    ok: bool
    vault_token: str
    detail: str

class PushResponse(MessageResponse):
    status: PushStatuses

class PullResponse(MessageResponse):
    vault_data: EncryptedUserVault | None = None
    status: PullStatuses
    
class DeleteVaultResponse(MessageResponse):
    vault_id: int
    vault_name: str