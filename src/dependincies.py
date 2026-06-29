from datetime import datetime, timezone
from typing import AsyncIterator

from fastapi import Body, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.session_dao import SessionDao
from src.schemas.db_schema import UserFields, UserRoles
from src.dao.userDao import UserDao
from src.schemas.jwt import JWTDecodedData
from src.services.jwt_service import JWT_Service
from src.schemas.base import ChangePasswordSchema
from src.core.settings import get_settings
from src.core.database import async_session
from src.core.logger import get_logger


logger = get_logger(__name__)

security = HTTPBearer()




def get_jwt_service() -> JWT_Service:
    settings = get_settings()
    return JWT_Service(
    secret_key=settings.SECRET_KEY,
    algoritm="HS256",
    access_token_expire_in_min=30,
    refresh_token_expire_in_days=3
)

async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session() as db:
        yield db



async def verify_user(
    db = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_service: JWT_Service = Depends(get_jwt_service)
) -> JWTDecodedData:
    try:
        token_data = jwt_service.verify_token(token=credentials.credentials)

        user_dao = UserDao(session=db)
        user = await user_dao.get_user_by_field(field=UserFields.ID, value=int(token_data.sub))
        if user is None:
            raise HTTPException(401, "Wrong user data")
        if not user.is_active:
            raise HTTPException(401, "This account is not active")
        
        dao = SessionDao(session=db)
        session = await dao.get_session(session_id=token_data.sid)
        if session is None:
            raise HTTPException(401, "Wrong session id, session does not exists")
        if not session.is_active:
            raise HTTPException(401, "Session was expired, try to login")
    
        if user.id != int(token_data.sub):
            raise HTTPException(401, "Invalid session binding")
    
        now = datetime.now(timezone.utc)
        if now > session.expires_at:
            raise HTTPException(401, "Token was expired")
    
        return token_data
    except HTTPException as e:
        logger.exception(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    

async def verify_refresh_token(
    request: Request,
    db = Depends(get_db),
    jwt_service: JWT_Service = Depends(get_jwt_service),
) -> JWTDecodedData:
    try:
        refresh = request.headers.get("Refresh")
        if refresh is None:
            raise HTTPException(401, detail="No Refresh token")
        token_data = jwt_service.verify_token(token=refresh)

        user_dao = UserDao(session=db)
        user = await user_dao.get_user_by_field(field=UserFields.ID, value=int(token_data.sub))
        if user is None:
            raise HTTPException(401, "Wrong user data")
        if not user.is_active:
            raise HTTPException(401, "This accaunt is not active")
        
        dao = SessionDao(session=db)
        session = await dao.get_session(session_id=token_data.sid)
        if session is None:
            raise HTTPException(401, "Wrong session id, session does not exists")
        if not session.is_active:
            raise HTTPException(401, "Session was expired, try to login")
    
        if user.id != int(token_data.sub):
            raise HTTPException(401, "Invalid session binding")
    
        now = datetime.now(timezone.utc)
        if now > session.expires_at:
            raise HTTPException(401, "Token was expired")
    
        return token_data
    except HTTPException as e:
        logger.exception(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    

async def check_admin(
    data = Depends(verify_user),
    db = Depends(get_db)
) -> JWTDecodedData:
    user_dao = UserDao(session=db)
    user_with_role = await user_dao.get_user_with_role(user_id=int(data.sub))
    if not user_with_role:
        raise HTTPException(401, "You do not have permission for this page")
    if user_with_role.role != UserRoles.ADMIN:
        raise HTTPException(401, "You do not have permission for this page")
    
    return data    
    
async def validate_change_passwords(
    current_password: str = Body(..., min_length=4, max_length=32),
    new_password: str = Body(..., min_length=4, max_length=32)
    ) -> ChangePasswordSchema:
    if " " in current_password.strip() or " " in new_password.strip():
        raise HTTPException(422, "The password must not contain spaces")
    return ChangePasswordSchema(
        current_password=current_password,
        new_password=new_password
    )
        
    
    
###############################
            # WEB
###############################
async def verify_web_user(
    request: Request,
    db = Depends(get_db)    
) -> JWTDecodedData:
    try:
        bearer_token = request.cookies.get("bearer_token")
        if bearer_token is None:
            raise HTTPException(401, "No bearer token")
        jwt_servise = get_jwt_service()
        token_data = jwt_servise.verify_token(token=bearer_token)
        user_dao = UserDao(session=db)
        user = await user_dao.get_user_by_field(field=UserFields.ID, value=int(token_data.sub))
        if user is None:
            raise HTTPException(401, "Wrong user data")
        if not user.is_active:
            raise HTTPException(401, "This account is not active")
        
        dao = SessionDao(session=db)
        session = await dao.get_session(session_id=token_data.sid)
        if session is None:
            raise HTTPException(401, "Wrong session id, session does not exists")
        if not session.is_active:
            raise HTTPException(401, "Session was expired, try to login")
    
        if user.id != int(token_data.sub):
            raise HTTPException(401, "Invalid session binding")
    
        now = datetime.now(timezone.utc)
        if now > session.expires_at:
            raise HTTPException(401, "Token was expired")
    
        return token_data
    except HTTPException as e:
        logger.exception(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(401, "Invalid token")
    
async def verify_web_refresh_token(
    request: Request,
    db = Depends(get_db)
) -> JWTDecodedData:
    try:
        refresh_token = request.cookies.get("refresh_token")
        if refresh_token is None:
            raise HTTPException(401, "No bearer token")

        jwt_servise = get_jwt_service()
        token_data = jwt_servise.verify_token(token=refresh_token)
        
        user_dao = UserDao(session=db)
        user = await user_dao.get_user_by_field(field=UserFields.ID, value=int(token_data.sub))
        if user is None:
            raise HTTPException(401, "Wrong user data")
        if not user.is_active:
            raise HTTPException(401, "This accaunt is not active")
        
        dao = SessionDao(session=db)
        session = await dao.get_session(session_id=token_data.sid)
        if session is None:
            raise HTTPException(401, "Wrong session id, session does not exists")
        if not session.is_active:
            raise HTTPException(401, "Session was expired, try to login")
    
        if user.id != int(token_data.sub):
            raise HTTPException(401, "Invalid session binding")
    
        now = datetime.now(timezone.utc)
        if now > session.expires_at:
            raise HTTPException(401, "Token was expired")
    
        return token_data
    except HTTPException as e:
        logger.exception(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    
