from enum import StrEnum

from pydantic import BaseModel



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
    telegram_id: int