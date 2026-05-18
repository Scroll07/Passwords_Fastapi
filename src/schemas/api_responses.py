from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel

from src.schemas.jwt import EncodedToken




class BackupData(BaseModel):
    id: int
    name: str
    rows: int
    created_at: datetime
    
class TypeResponses(StrEnum):
    MESSAGE = "message"
    LOGIN = "login"
    BACKUPS = "backups"
    DOWNLOAD = "download"
    REFRESH = "refresh"


# ===================================
#               Responses
# ===================================
class MessageResponse(BaseModel):
    ok: bool
    message: str
    type: TypeResponses = TypeResponses.MESSAGE

class LoginResponse(MessageResponse):
    bearer_token: EncodedToken
    refresh_token: EncodedToken
    type: TypeResponses = TypeResponses.LOGIN

class RefreshResponse(LoginResponse):
    type: TypeResponses = TypeResponses.REFRESH

class BackupsResponse(MessageResponse):
    backups: list[BackupData]
    type: TypeResponses = TypeResponses.BACKUPS
    
# class DownloadResponse(BaseModel):
#     vault_data: EncryptedUserVault
#     type: TypeResponses = TypeResponses.DOWNLOAD