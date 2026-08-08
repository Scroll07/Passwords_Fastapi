    
from datetime import datetime

from pydantic import BaseModel

from backend.schemas.db_schema import UserRoles, UserInDb


class UserWithRole(BaseModel):
    user: UserInDb
    role: UserRoles
    
class UserData(BaseModel):
    id: int
    username: str
    telegram_id: int | None
    role: str
    is_active: bool
    created_at: datetime