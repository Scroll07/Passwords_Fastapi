from pydantic import BaseModel


class RegisterRequestData(BaseModel):
    username: str
    password: str
    telegram_id: int
    
class CreateUserInDb(BaseModel):
    username: str
    password_hash: str
    telegram_id: int