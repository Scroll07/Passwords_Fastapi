from fastapi import APIRouter, Depends

from src.dependincies import get_db
from src.core.schemas import RegisterRequestData
from src.dao.userDao import UserDao
from src.services.secrets import hash_password, verify_password

users = APIRouter()


@users.post("/register", status_code=201)
async def register_post(
    user_data: RegisterRequestData,
    
    db = Depends(get_db),
):
    password_hash = hash_password(user_data.password)
    user_data.password = password_hash
    
    dao = UserDao(db)
    new_user = await dao.create_user(user_data)

    return {"ok": True, "message": "New user was sucessfully created"}






