    
from pydantic import BaseModel

from src.schemas.db_schema import UserRoles, UserInDb


class UserWithRole(BaseModel):
    user: UserInDb
    role: UserRoles