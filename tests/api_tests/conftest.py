import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncIterator
from httpx import AsyncClient, ASGITransport

from main import app
from tests.conftest import TEST_ENGINE_URL
from backend.schemas.jwt import JWTDecodedData
from backend.schemas.db_schema import UserRoles, SessionType, CreateUserInDb
from backend.dao.role_dao import RoleDAO
from backend.models.model import Base, Users
import backend.dao.backupDao as dao_file
from backend.schemas.base import RegisterRequestData
from backend.dependencies import get_db
from backend.api_dependencies import verify_user, verify_refresh_token
from backend.dao.userDao import UserDao
from backend.dao.backupDao import BackupDao
import backend.dao.backupDao as BackupDaoDir

@pytest_asyncio.fixture
async def create_one_backup(test_user, tmp_path, monkeypatch, db_session):
    async def _inner():
        monkeypatch.setattr(BackupDaoDir, "BACKUPS", tmp_path)
        dao = BackupDao(db_session)
        async with dao.create_backup(
            user_id=test_user.id,
            filename="Backup.json",
            rows=4,
            name="Backup name",
            pinned=False
        ) as backup:
            with open(backup.path, "wb") as f:
                f.write(b"My backup data") 
            return backup
    return _inner
    
@pytest_asyncio.fixture
async def test_backup(test_user, db_session: AsyncSession, 
    tmp_path, 
    monkeypatch
):
    monkeypatch.setattr(BackupDaoDir, "BACKUPS", tmp_path)
    
    dao = BackupDao(db_session)
    async with dao.create_backup(
        user_id=test_user.id,
        filename="Backup.json",
        rows=4,
        name="Backup name",
        pinned=False
    ) as backup:
        with open(backup.path, "wb") as f:
            f.write(b"My backup data") 
        
        yield backup
    
    
@pytest_asyncio.fixture
async def register_test_user(client):
    data = RegisterRequestData(username="test", password="test", telegram_id=129374758)
    response = await client.post(
        url="/api/register",
        json=data.model_dump()
    )
    print(response.json())
    assert response.status_code == 201
    return data

@pytest_asyncio.fixture
async def override_db(db_session):
    async def overrides_get_db():
        return db_session

    
    app.dependency_overrides[get_db] = overrides_get_db 

    yield

    app.dependency_overrides.clear()


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
def jwt_bearer_mock(test_user):
    token_data = JWTDecodedData(
            sub=str(test_user.id),
            sid=123,
            exp=123,
            type=SessionType.BEARER
        )
    def mock_verify_user():
        return token_data

    app.dependency_overrides[verify_user] = mock_verify_user

    yield token_data

    app.dependency_overrides.clear()

@pytest.fixture
def jwt_refresh_mock(test_user):
    token_data = JWTDecodedData(
            sub=str(test_user.id),
            sid=123,
            exp=123,
            type=SessionType.REFRESH
        )
    def mock_verify_user():
        return token_data

    app.dependency_overrides[verify_refresh_token] = mock_verify_user

    yield token_data

    app.dependency_overrides.clear()
    

@pytest_asyncio.fixture
async def test_user(init_db, db_session: AsyncSession) -> Users:
    role_dao = RoleDAO(session=db_session)
    user_role = await role_dao.get_role(role_name=UserRoles.USER)
    assert user_role is not None
    dao = UserDao(db_session)
    user_data = CreateUserInDb(
        username="test",
        password_hash="password_hash",
        telegram_id=987654321
    )
    new_user = await dao.create_user(
        user_data=user_data,
        role_id=user_role.id
    )
    return new_user