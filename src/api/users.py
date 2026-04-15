from fastapi import APIRouter, Depends, HTTPException

from src.dependincies import get_db
from schemas.base import RegisterRequestData, LoginRequest, GetUserFields
from src.dao.userDao import UserDao
from src.services.secrets import hash_password, verify_password
from src.services.secrets import jwt_service

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


@users.post("/login")
async def login_post(
    user_data: LoginRequest,
    db = Depends(get_db),
):
    try:
        dao = UserDao(db)
        user = await dao.get_user_by_field(GetUserFields.USERNAME, user_data.username)
        if not user:
            raise HTTPException(401, "Wrong user data")
            
        
        if not verify_password(user_data.password, user.password_hash):
            raise HTTPException(401, "Wrong user data")

        token = jwt_service.create_access_token(user_id=user.id)
        
        return {
            "ok": True,
            "access_token": token.access_token,
            "token_type": token.token_type,
            "message": "Success login"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, "Internal server error")
