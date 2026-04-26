from fastapi import APIRouter, Depends, HTTPException

from src.dependincies import get_db
from src.schemas.base import RegisterRequestData, LoginRequest, GetUserFields
from src.dao.userDao import UserDao
from src.services.secrets import hash_password, verify_password
from src.services.secrets import jwt_service
from src.core.logger import get_logger


logger = get_logger(__name__)

users = APIRouter()


@users.post("/register", status_code=201)
async def register_post(
    user_data: RegisterRequestData,
    db=Depends(get_db),
):
    try:
        password_hash = hash_password(user_data.password)
        user_data.password = password_hash

        dao = UserDao(db)

        exist_username = await dao.get_user_by_field(
            GetUserFields.USERNAME, user_data.username
        )
        if exist_username:
            raise HTTPException(409, detail="User with this username alredy exists")

        if user_data.telegram_id is not None:
            exist_telegram_id = await dao.get_user_by_field(
            GetUserFields.TELEGRAM_ID, user_data.telegram_id
        )
            if exist_telegram_id:
                raise HTTPException(409, detail="User with this telegram id alredy exists")

        await dao.create_user(user_data)

        return {"ok": True, "message": "New user was sucessfully created"}

    except HTTPException as e:
        logger.warning(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")


@users.post("/login")
async def login_post(
    user_data: LoginRequest,
    db=Depends(get_db),
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
            "message": "Success login",
        }
    except HTTPException as e:
        logger.warning(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
