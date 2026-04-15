from pydantic import BaseModel
from enum import StrEnum

class RegisterRequestData(BaseModel):
    username: str
    password: str
    telegram_id: int
    
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
    ID="id"
    USERNAME="username"
    TELEGRAM_ID="telegram_id"