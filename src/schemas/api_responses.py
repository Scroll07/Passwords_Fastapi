from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel

from src.schemas.jwt import EncodedToken
from src.schemas.base import BackupData




    
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
    

