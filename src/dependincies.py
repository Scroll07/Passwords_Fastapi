from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.database import async_session
from src.services.secrets import jwt_service
from src.core.logger import get_logger

logger = get_logger(__name__)

security = HTTPBearer()


async def get_db():
    async with async_session() as db:
        yield db

        await db.close()


async def verify_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    try:
        token = credentials.credentials
        user_id = jwt_service.verify_token(token)
        return user_id
    except Exception:
        raise HTTPException(401, "Invalid token")
