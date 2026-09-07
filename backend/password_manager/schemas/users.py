from pydantic import BaseModel


class UserData(BaseModel):
    username: str
    master_password: str