from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.settings import get_settings
from backend.core.database import async_session
from backend.services.jwt_service import JWT_Service




def get_jwt_service() -> JWT_Service:
    settings = get_settings()
    return JWT_Service(
    secret_key=settings.SECRET_KEY,
    algoritm="HS256",
    access_token_expire_in_min=30,
    refresh_token_expire_in_days=3,
    vault_token_expire_in_mins=30
)

async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session() as db:
        yield db

