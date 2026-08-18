
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dao.session_dao import SessionDao
from backend.schemas.jwt import JWTDecodedData
from backend.services.jwt_service import JWT_Service, create_token_and_session
from backend.schemas.api_responses import MessageResponse
from backend.dependencies import get_db, get_jwt_service
from backend.schemas.base import RegisterRequestData, WebChangePasswordSchema
from backend.schemas.db_schema import UserFields, SessionType
from backend.dao.userDao import UserDao
from backend.services.secrets import hash_password, verify_password
from backend.core.logger import get_logger
from backend.services.cookies import add_bearer_cookie, add_refresh_cookie
from backend.web_dependencies import verify_web_refresh_token, verify_web_user, web_validate_change_passwords

logger = get_logger(__name__)

web_users = APIRouter()

#==============================
#            API   
#==============================

@web_users.post("/login", response_class=RedirectResponse)
async def web_login_post(
    user_data: RegisterRequestData,
    db=Depends(get_db),
    jwt_service: JWT_Service = Depends(get_jwt_service),
):
    try:
        dao = UserDao(db)
        user = await dao.get_user_by_field(UserFields.USERNAME, user_data.username)
        if not user:
            raise HTTPException(401, "Wrong user data")

        if not verify_password(user_data.password, user.password_hash):
            raise HTTPException(401, "Wrong user data")

        bearer_token = await create_token_and_session(
            session=db,
            jwt_service=jwt_service,
            user_id=user.id,
            token_type=SessionType.BEARER
        )
        refresh_token = await create_token_and_session(
            session=db,
            jwt_service=jwt_service,
            user_id=user.id,
            token_type=SessionType.REFRESH
        )
        
        content = MessageResponse(
            ok=True,
            detail="login",
        )
        response = JSONResponse(
            content=content.model_dump(),
        )
        add_bearer_cookie(response=response, value=bearer_token.token)
        add_refresh_cookie(response=response, value=refresh_token.token)
        
        await db.commit()
            
        return response
    except HTTPException as e:
        logger.exception(e)        
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")

@web_users.post("/logout")
async def web_logout(
    db: AsyncSession = Depends(get_db),
    data: JWTDecodedData = Depends(verify_web_user)
):    
    session_dao = SessionDao(session=db)

    await session_dao.make_unactive_session(user_id=int(data.sub))
    response = RedirectResponse(
        url="/login",
        status_code=303
        )
    response.delete_cookie(key="bearer_token", httponly=True, samesite="lax")
    response.delete_cookie(key="refresh_token", httponly=True, samesite="lax")
    
    await db.commit()
    return response

@web_users.get("/refresh")
async def web_refresh_get(
    token_data: JWTDecodedData = Depends(verify_web_refresh_token),
    db=Depends(get_db),
    jwt_service: JWT_Service = Depends(get_jwt_service),
):
    try:
        bearer_token = await create_token_and_session(
            session=db,
            jwt_service=jwt_service,
            user_id=int(token_data.sub),
            token_type=SessionType.BEARER
        )
        refresh_token = await create_token_and_session(
            session=db,
            jwt_service=jwt_service,
            user_id=int(token_data.sub),
            token_type=SessionType.REFRESH
        )
        
        content = {
            "ok": True,
            "detail": "Tokens were successully refreshed"
        } 
        
        response = JSONResponse(
            content=content
        )
        add_bearer_cookie(response=response, value=bearer_token.token)
        add_refresh_cookie(response=response, value=refresh_token.token)
        
        await db.commit()
        return response
    
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    

@web_users.post("/change-password")
async def web_change_password(
    data: WebChangePasswordSchema = Depends(web_validate_change_passwords), 
    db=Depends(get_db),
):
    try:
        dao = UserDao(session=db)
        user = await dao.get_user_by_field(field=UserFields.USERNAME, value=data.username)
        if user is None:
            logger.exception(f"User with this username={data.username} does not exist")
            raise HTTPException(404, "User with this username does not exist")
        
        if not verify_password(password=data.current_password, password_hash=user.password_hash):
            raise HTTPException(401, "Wrong user data")
        
        new_hash = hash_password(password=data.new_password)
        await dao.change_password(user=user, new_hash=new_hash)
        
        response = MessageResponse(
            ok=True,
            detail="Your password was successuflly changed",
        )
        return response
    
    except HTTPException as e:
        logger.exception(e)        
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    


@web_users.get("/me")
async def web_me(
    data: JWTDecodedData = Depends(verify_web_user), 
    db=Depends(get_db),
):
    user_id = int(data.sub)
    dao = UserDao(session=db)
    user_data = await dao.get_user_data(user_id=user_id)
    if not user_data:
        return {"ok": False, "detail": "There is no data of this user id"}
    return {
        "ok": True,
        "data": user_data.model_dump()
    }
    