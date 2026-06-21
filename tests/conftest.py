from typing import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from src.schemas.jwt import JWTDecodedData, TokenType
from src.schemas.db_schema import UserRoles
from src.dao.role_dao import RoleDAO
from src.models.model import Base, Users
from main import app
from src.dependincies import get_db, verify_user, verify_refresh_token, get_jwt_service
from src.services.jwt_service import create_token_and_session, JWT_Service


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



