from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, ConfigDict, computed_field

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


class CreateVaultData(BaseModel):
    name: str
    master_password: str

    @field_validator('name')
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not (1 < len(value) < 32):
            raise ValueError("Wrong length of vault name")
        return value
    
    @field_validator('master_password')
    def validate_master_password(cls, value: str) -> str:
        value = value.strip()
        if not (4 < len(value) < 32):
            raise ValueError("Wrong length of vault master password")
        if ' ' in value:
           raise ValueError("Master password must not contain spaces") 
        return value

class VaultData(BaseModel):
    id: int
    name: str
    entries: int
    pinned: bool
    created_at: datetime 

    @computed_field
    @property
    def created_at_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        
    model_config = ConfigDict(from_attributes=True)

class UserData(BaseModel):
    username: str
    password_hash: str
    telegram_id: int | None

class SortByBackups(StrEnum):
    NAME = "name"
    ROWS = "rows"
    CREATED_AT = "created_at"
    
class SortByVaults(StrEnum):
    NAME = "name"
    ENTRIES = "entries"
    CREATED_AT = "created_at"
    
    
class BackupData(BaseModel):
    id: int
    name: str
    rows: int
    pinned: bool
    created_at: datetime 

    @computed_field
    @property
    def created_at_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        
    model_config = ConfigDict(from_attributes=True)

class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str

class WebChangePasswordSchema(ChangePasswordSchema):
    # current_password: str
    # new_password: str
    username: str