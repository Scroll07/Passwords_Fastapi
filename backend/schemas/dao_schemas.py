    
from pydantic import BaseModel

from backend.schemas.db_schema import UserRoles, UserInDb


class UserWithRole(BaseModel):
    user: UserInDb
    role: UserRoles