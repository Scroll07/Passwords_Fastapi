from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.schemas.api_responses import LoginResponse, MessageResponse, RefreshResponse
from src.dependincies import get_db, verify_refresh_token, get_jwt_service, verify_user
from src.schemas.base import RegisterRequestData, LoginRequest, GetUserFields
from src.dao.userDao import UserDao
from src.services.secrets import hash_password, verify_password
from src.core.logger import get_logger
from src.services.cookies import add_bearer_cookie, add_refresh_cookie

logger = get_logger(__name__)

users = APIRouter()

#==============================
#            API   
#==============================
@users.post("/api/register", status_code=201)
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


@users.post("/api/login")
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
    
    
@users.get("/api/refresh")
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
    

@users.patch("/api/change-password")
async def change_password(
    current_password: str = Body(...),
    new_password: str = Body(...), 
    user_id = Depends(verify_user),
    db = Depends(get_db)
):
    try:
        dao = UserDao(session=db)
        user = await dao.get_user_by_field(field=GetUserFields.ID, value=user_id)
        if user is None:
            logger.exception(f"User with this user_id={user_id} does not exist")
            raise HTTPException(404, "User with this user_id does not exist")
        
        if not verify_password(password=current_password, password_hash=user.password_hash):
            raise HTTPException(401, "Wrong user data")
        
        new_hash = hash_password(password=new_password)
        await dao.change_password(user=user, new_hash=new_hash)
        
        response = MessageResponse(
            ok=True,
            detail="Your password was successuflly changed",
        )
        return response
    
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    


#==============================
#            WEB    
#==============================
from src.dependincies import verify_web_refresh_token

@users.post("/web/register", status_code=201)
async def web_register_post(
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


@users.post("/web/login")
async def web_login_post(
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
        
        content = {
            "ok": True,
            "detail": "Success login"
        } 
        
        response = JSONResponse(
            content=content
        )
        add_bearer_cookie(response=response, value=bearer_token.token)
        add_refresh_cookie(response=response, value=refresh_token.token)
        
        return response
    
    except HTTPException as e:
        logger.warning(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    
    
@users.get("/web/refresh")
async def web_refresh_get(
    user_id = Depends(verify_web_refresh_token)
):
    try:
        jwt_service = get_jwt_service()
        bearer_token = jwt_service.create_access_token(user_id=user_id)
        refresh_token = jwt_service.create_refresh_token(user_id=user_id)
        
        content = content = {
            "ok": True,
            "detail": "Tokens were succussefully refreshed"
        } 
        response = JSONResponse(
            content=content
        )
        add_bearer_cookie(response=response, value=bearer_token.token)
        add_refresh_cookie(response=response, value=refresh_token.token)
        
        return response
    
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")