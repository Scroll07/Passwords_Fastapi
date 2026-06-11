from typing import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from src.schemas.db_schema import UserRoles
from src.dao.role_dao import RoleDAO
from src.schemas.base import RegisterRequestData
from src.models.model import Base, Users
from main import app
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
async def init_db(db_session: AsyncSession):
    roles_dao = RoleDAO(session=db_session)
        
    roles = await roles_dao.initialize_roles()
    
    await db_session.commit()



@pytest_asyncio.fixture
async def client(override_db, init_db) -> AsyncIterator[AsyncClient]:
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
async def test_user(init_db, db_session: AsyncSession) -> Users:
    role_dao = RoleDAO(session=db_session)
    user_role = await role_dao.get_role(role_name=UserRoles.USER)
    assert user_role is not None
    user = Users(
        username="test_username",
        password_hash="hashed_password",
        telegram_id=1910592094,
        role_id=user_role.id
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.commit()
    return user
