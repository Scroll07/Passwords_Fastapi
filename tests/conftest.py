from typing import AsyncGenerator, AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from src.schemas.base import RegisterRequestData
from src.models.model import Base
from src.main import app
from src.dependincies import get_db, verify_user, verify_refresh_token


TEST_ENGINE_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db"

@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    test_engine = create_async_engine(url=TEST_ENGINE_URL)
    test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with test_session() as session:
        yield session


@pytest_asyncio.fixture
async def override_db():
    test_engine = create_async_engine(url=TEST_ENGINE_URL)
    test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def overrides_get_db():
        async with test_session() as session:
                yield session

    
    app.dependency_overrides[get_db] = overrides_get_db 

    yield

    app.dependency_overrides.clear()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    

@pytest_asyncio.fixture
async def client(override_db) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def jwt_bearer_mock():
    user_id = 1
    def mock_verify_user():
        return user_id

    app.dependency_overrides[verify_user] = mock_verify_user

    yield user_id

    app.dependency_overrides.clear()

@pytest.fixture
def jwt_refresh_mock():
    user_id = 1
    def mock_verify_user():
        return user_id

    app.dependency_overrides[verify_refresh_token] = mock_verify_user

    yield user_id

    app.dependency_overrides.clear()
    
    
@pytest_asyncio.fixture
async def create_test_user(client: AsyncClient, jwt_bearer_mock) -> None:
    user_id = jwt_bearer_mock
    data = RegisterRequestData(
        username="test_user", password="pass", telegram_id=1910592094
    )
    await client.post(
        url="/register",
        json=data.model_dump()
    )

