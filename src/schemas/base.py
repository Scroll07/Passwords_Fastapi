from datetime import datetime

from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import StrEnum


##########################
#       REQUESTS
##########################

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
#=============================
#=============================
#=============================

class DownloadRequest(BaseModel):
    backup_id: int
    
class DeleteRequest(BaseModel):
    backup_id: int

class UploadRequest(BaseModel):
    name: str = Field(max_length=24)
    rows_count: int






class UserData(BaseModel):
    username: str
    password_hash: str
    telegram_id: int | None


    
class BackupData(BaseModel):
    id: int
    name: str
    rows: int
    pinned: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str