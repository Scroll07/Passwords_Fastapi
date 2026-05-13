from datetime import datetime

from pydantic import BaseModel
from enum import StrEnum


##########################
#       REQUESTS
##########################


class RegisterRequestData(BaseModel):
    username: str
    password: str
    telegram_id: int | None = None

class DownloadRequest(BaseModel):
    backup_id: int
    
class DeleteRequest(BaseModel):
    backup_id: int

class UploadRequest(BaseModel):
    name: str
    rows_count: int




class CreateUserInDb(BaseModel):
    username: str
    password_hash: str
    telegram_id: int


class LoginRequest(BaseModel):
    username: str
    password: str


class UserData(BaseModel):
    username: str
    password_hash: str
    telegram_id: int | None


class GetUserFields(StrEnum):
    ID = "id"
    USERNAME = "username"
    TELEGRAM_ID = "telegram_id"
    
class BackupData(BaseModel):
    id: int
    name: str
    rows: int
    created_at: datetime

    