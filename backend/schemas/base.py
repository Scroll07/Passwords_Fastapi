from pydantic import BaseModel

class UserData(BaseModel):
    username: str
    password_hash: str
    telegram_id: int | None

class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str

class WebChangePasswordSchema(ChangePasswordSchema):
    # current_password: str
    # new_password: str
    username: str