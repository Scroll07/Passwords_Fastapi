from datetime import datetime, timedelta
from typing import AsyncIterator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from backend.schemas.jwt import JWTDecodedData
from backend.schemas.db_schema import SessionType
from backend.dependencies import get_jwt_service
from backend.services.jwt_service import JWT_Service
from backend.core.settings import Settings



TEST_ENGINE_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db"

TEST_SECRET_KEY = "wjeQv9BfnQYKPSB-gjvmfujfh3jri3j0"

@pytest.fixture(autouse=True)
def mock_secret_key(monkeypatch):
    monkeypatch.setattr(Settings, "SECRET_KEY", TEST_SECRET_KEY)


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    test_engine = create_async_engine(url=TEST_ENGINE_URL)
    test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with test_session() as session:
        await session.execute(text("DELETE FROM users CASCADE"))
        await session.execute(text("DELETE FROM roles CASCADE"))
        await session.execute(text("DELETE FROM sessions CASCADE"))
        await session.execute(text("DELETE FROM backups CASCADE"))
        await session.execute(text("DELETE FROM vaults CASCADE"))
        await session.commit()
        
        yield session
        
    await test_engine.dispose()


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
        type=SessionType.BEARER
    )
    token = jwt_service.create_token(data=data)
    return token.token