from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from src.schemas.api_responses import LoginResponse, MessageResponse, RefreshResponse
from src.dependincies import get_db, get_jwt_service, verify_web_user
from src.schemas.base import RegisterRequestData, LoginRequest, GetUserFields
from src.dao.userDao import UserDao
from src.services.secrets import hash_password, verify_password
from src.core.logger import get_logger
from src.services.cookies import add_bearer_cookie, add_refresh_cookie
from src.dependincies import verify_web_refresh_token

logger = get_logger(__name__)

web_users = APIRouter()


#==============================
#            WEB    
#==============================

@web_users.post("/register", status_code=201)
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


@web_users.post("/login")
async def web_login_post(
    request: Request,
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
    
    
@web_users.get("/logout")
async def logout():
    response = RedirectResponse(url="/web/login")
    response.delete_cookie(key="bearer_token", httponly=True, samesite="lax")
    response.delete_cookie(key="refresh_token", httponly=True, samesite="lax")
    return response
    
    
    
    
    
    
@web_users.get("/refresh")
async def web_refresh_get(
    user_id = Depends(verify_web_refresh_token)
):
    try:
        if user_id is None:
            return RedirectResponse(url="/web/login")
        
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