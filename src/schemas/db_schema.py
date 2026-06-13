from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, ConfigDict


class UserRoles(StrEnum):
    ADMIN = "admin"
    USER = "user"
    # MANAGER = "manager"
    # GUEST = "guest"
    
class UserFields(StrEnum):
    ID = "id"
    USERNAME = "username"
    TELEGRAM_ID = "telegram_id"


class CreateUserInDb(BaseModel):
    username: str
    password_hash: str
    telegram_id: int | None = None
    
class UserInDb(BaseModel):
    id: int
    username: str
    password_hash: str
    telegram_id: int | None
    role_id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)