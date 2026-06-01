from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.schemas.api_responses import LoginResponse, MessageResponse, RefreshResponse
from src.dependincies import get_db, verify_refresh_token, get_jwt_service, verify_user, validate_change_passwords
from src.schemas.base import ChangePasswordSchema, RegisterRequestData, LoginRequest, GetUserFields
from src.dao.userDao import UserDao
from src.services.secrets import hash_password, verify_password
from src.core.logger import get_logger

logger = get_logger(__name__)

api_users = APIRouter()

#==============================
#            API   
#==============================
@api_users.post("/register", status_code=201)
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

        response = MessageResponse(
            ok=True,
            detail="New user was sucessfully created"
        )
        return response

    except HTTPException as e:
        logger.warning(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")


@api_users.post("/login")
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
        
        response = LoginResponse(
            ok=True,
            detail="Success login",
            bearer_token=bearer_token,
            refresh_token=refresh_token
        )
        
        return response
    
    except HTTPException as e:
        logger.warning(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    
    
@api_users.get("/refresh")
async def refresh_get(
    user_id = Depends(verify_refresh_token)
):
    try:
        jwt_service = get_jwt_service()
        bearer_token = jwt_service.create_access_token(user_id=user_id)
        refresh_token = jwt_service.create_refresh_token(user_id=user_id)
        
        response = RefreshResponse(
            ok=True,
            detail="Tokens were successfully refreshed",
            bearer_token=bearer_token,
            refresh_token=refresh_token
        )
        return response
    
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    

@api_users.patch("/change-password")
async def change_password(
    data: ChangePasswordSchema = Depends(validate_change_passwords), 
    user_id = Depends(verify_user),
    db = Depends(get_db)
):
    try:
        dao = UserDao(session=db)
        user = await dao.get_user_by_field(field=GetUserFields.ID, value=user_id)
        if user is None:
            logger.exception(f"User with this user_id={user_id} does not exist")
            raise HTTPException(404, "User with this user_id does not exist")
        
        if not verify_password(password=data.current_password, password_hash=user.password_hash):
            raise HTTPException(401, "Wrong user data")
        
        new_hash = hash_password(password=data.new_password)
        await dao.change_password(user=user, new_hash=new_hash)
        
        response = MessageResponse(
            ok=True,
            detail="Your password was successuflly changed",
        )
        return response
    
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    


