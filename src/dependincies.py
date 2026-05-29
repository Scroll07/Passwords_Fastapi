from typing import AsyncIterator

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession


from src.core.settings import get_settings
from src.core.database import async_session
from src.services.secrets import JWT, ALGORITM
from src.core.logger import get_logger


logger = get_logger(__name__)

security = HTTPBearer()




def get_jwt_service() -> JWT:
    settings = get_settings()
    return JWT(algoritm=ALGORITM, secret_key=settings.SECRET_TOKEN_KEY)

async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session() as db:
        yield db



async def verify_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    try:
        jwt_service = get_jwt_service()
        token = credentials.credentials
        user_id = jwt_service.verify_token(token)
        return user_id
    except Exception as e:
        logger.exception(e)
        raise HTTPException(401, "Invalid token")
    

async def verify_refresh_token(
    request: Request,
) -> int:
    try:
        refresh = request.headers.get("Refresh")
        if refresh is None:
            raise HTTPException(401, detail="No Refresh token")
        jwt_service = get_jwt_service()
        user_id = jwt_service.verify_token(token=refresh)
        return user_id
    except HTTPException as e:
        logger.exception(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(401, "Invalid token")
    
    
async def verify_web_user(request: Request) -> int:
    try:
        bearer_token = request.cookies.get("bearer_token")
        if bearer_token is None:
            raise HTTPException(401, "No access token")
        jwt_servise = get_jwt_service()
        user_id = jwt_servise.verify_token(token=bearer_token)
        return user_id
    except HTTPException as e:
        logger.exception(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(401, "Invalid token")
    
async def verify_web_refresh_token(request: Request) -> int:
    try:
        refresh_token = request.cookies.get("refresh_token")
        if refresh_token is None:
            raise HTTPException(401, "No access token")
        jwt_servise = get_jwt_service()
        user_id = jwt_servise.verify_token(token=refresh_token)
        return user_id
    except HTTPException as e:
        logger.exception(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(401, "Invalid token")
    
