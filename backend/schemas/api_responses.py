from enum import StrEnum
from pydantic import BaseModel

from backend.schemas.jwt import EncodedToken
from backend.schemas.base import BackupData
from backend.schemas.db_schema import BackupStats


class RedirectPaths(StrEnum):
    DASHBOARD = "dashboard"
    
    
class TypeResponses(StrEnum):
    MESSAGE = "message"
    LOGIN = "login"
    BACKUPS = "backups"
    DOWNLOAD = "download"
    REFRESH = "refresh"
    STATS = "stats"


# ===================================
#               Responses
# ===================================
class MessageResponse(BaseModel):
    ok: bool
    detail: str
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
    
class BackupStatsResponse(BaseModel):
    ok: bool
    stats: BackupStats
    type: TypeResponses = TypeResponses.STATS
    
    
class VaultStatusResponse(BaseModel):
    detail: str
    access: bool