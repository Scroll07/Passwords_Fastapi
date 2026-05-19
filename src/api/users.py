from fastapi import APIRouter, Depends, HTTPException

from src.schemas.api_responses import LoginResponse
from src.dependincies import get_db, verify_refresh_token, get_jwt_service
from src.schemas.base import RegisterRequestData, LoginRequest, GetUserFields
from src.dao.userDao import UserDao
from src.services.secrets import hash_password, verify_password
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

        jwt_service = get_jwt_service()
        bearer_token = jwt_service.create_access_token(user_id=user.id)
        refresh_token = jwt_service.create_refresh_token(user_id=user.id)
        
        # response = LoginResponse(
        #     ok=True,
        #     detail="Success login",
        #     bearer_token=bearer_token,
        #     refresh_token=refresh_token
        # )
        
        return {
            "ok": True,
            "bearer_token": bearer_token,
            "refresh_token": refresh_token,
            "message": "Success login",
        }
    except HTTPException as e:
        logger.warning(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    
    
@users.get("/refresh")
async def refresh_get(
    user_id = Depends(verify_refresh_token)
):
    try:
        jwt_service = get_jwt_service()
        bearer_token = jwt_service.create_access_token(user_id=user_id)
        refresh_token = jwt_service.create_refresh_token(user_id=user_id)
            
        return {
                "ok": True,
                "bearer_token": bearer_token,
                "refresh_token": refresh_token,
                "message": "Tokens were successfully refreshed",
            }
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
        