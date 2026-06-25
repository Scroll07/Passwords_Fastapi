from datetime import datetime, timedelta
from typing import AsyncIterator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.schemas.jwt import JWTDecodedData, TokenType
from src.dependincies import get_jwt_service
from src.services.jwt_service import JWT_Service


TEST_ENGINE_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db"

@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    test_engine = create_async_engine(url=TEST_ENGINE_URL)
    test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with test_session() as session:
        yield session


@pytest.fixture
def jwt_service() -> JWT_Service:
    return get_jwt_service()


@pytest.fixture
def access_token(jwt_service: JWT_Service) -> str:
    expires = datetime.now() + timedelta(minutes=15)
    data = JWTDecodedData(
        sub="user_id",
        sid=0,
        exp=int(expires.timestamp()),
        type=TokenType.BEARER
    )
    token = jwt_service.create_access_token(data=data)
    return token.token