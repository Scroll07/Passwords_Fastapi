from fastapi import Body, HTTPException, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from backend.dao.session_dao import SessionDao
from backend.dependencies import get_db, get_jwt_service
from backend.schemas.db_schema import UserFields, UserRoles
from backend.dao.userDao import UserDao
from backend.schemas.jwt import JWTDecodedData, TokenType
from backend.services.jwt_service import JWT_Service, create_token_and_session
from backend.schemas.base import ChangePasswordSchema
from backend.core.logger import get_logger


logger = get_logger(__name__)

security = HTTPBearer()




async def _api_try_refresh_token(
    request: Request,
    db: AsyncSession,
    jwt_service: JWT_Service,
) -> JWTDecodedData:
    try:
        refresh = request.headers.get("Refresh")
        if refresh is None:
            raise HTTPException(401, detail="No Refresh token")
    
        refresh_token_data = jwt_service.verify_token(token=refresh)
        await create_token_and_session(
        session=db,
        jwt_service=jwt_service,
        user_id=int(refresh_token_data.sub),
        token_type=TokenType.REFRESH
    )   
        user_dao = UserDao(session=db)
        user = await user_dao.get_user_by_field(field=UserFields.ID, value=int(refresh_token_data.sub))
        if user is None:
            raise HTTPException(401, "Wrong user data")
        if not user.is_active:
            raise HTTPException(401, "This account is not active")
        
        dao = SessionDao(session=db)
        session = await dao.get_session(session_id=refresh_token_data.sid)
        if session is None:
            raise HTTPException(401, "Wrong session id, session does not exists")
        if not session.is_active:
            raise HTTPException(401, "Session was expired, try to login")
    
        if user.id != int(refresh_token_data.sub):
            raise HTTPException(401, "Invalid session binding")
        return refresh_token_data
    except InvalidTokenError as e:
        logger.exception(e)
        raise HTTPException(401, "Wrong refresh token")
    except Exception as e:
        logger.exception(e)
        raise e


async def verify_user(
    request: Request,
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

        return token_data
    except ExpiredSignatureError:
        logger.info("Bearer was expired, trying to verify refresh token")
        try:
            refresh_token_data = await _api_try_refresh_token(
                request=request,
                db=db,
                jwt_service=jwt_service
            )
            return refresh_token_data
        except InvalidTokenError as e:
            logger.exception(e)
            raise HTTPException(401, "Wrong refresh token") 
        
    except InvalidTokenError as e:
        logger.exception(e)
        raise HTTPException(401, "Wrong bearer token") 
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
    
    
        return token_data
    
    except InvalidTokenError as e:
        logger.exception(e)
        raise HTTPException(401, "Wrong refresh token")
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
    current_password = current_password.strip()
    new_password = new_password.strip()
    
    if " " in current_password or " " in new_password:
        raise HTTPException(400, "The password must not contain spaces")
    
    if current_password == new_password:
        raise HTTPException(400, "New password can not be the same as old password")
    
    return ChangePasswordSchema(
        current_password=current_password,
        new_password=new_password
    )