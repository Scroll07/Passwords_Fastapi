import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncIterator
from httpx import AsyncClient, ASGITransport

from main import app
from tests.conftest import TEST_ENGINE_URL
from src.schemas.jwt import JWTDecodedData, TokenType
from src.schemas.db_schema import UserRoles
from src.dao.role_dao import RoleDAO
from src.models.model import Base, Users
from src.dependincies import get_db, verify_user, verify_refresh_token, get_jwt_service
import src.dao.backupDao as dao_file
from src.schemas.base import RegisterRequestData


@pytest_asyncio.fixture
async def create_one_backup(test_user, tmp_path, monkeypatch, client):
    async def _inner():
        file_path = tmp_path / "test_backup.json"
        backup_data = b"My backup data"
        file_path.write_bytes(backup_data)

        monkeypatch.setattr(dao_file, "BACKUPS", tmp_path)

        with open(file_path, "rb") as f:
            response = await client.post(
                url="/api/backups/upload",
                files={"file": (file_path.name, f)},
                data={"name": "backup_name", "rows": 4}
            )
        assert response.status_code == 201
    return _inner
    
@pytest_asyncio.fixture
async def test_backup(test_user, tmp_path, monkeypatch, client):
    file_path = tmp_path / "test_backup.json"
    backup_data = b"My backup data"
    file_path.write_bytes(backup_data)

    monkeypatch.setattr(dao_file, "BACKUPS", tmp_path)

    with open(file_path, "rb") as f:
        response = await client.post(
            url="/api/backups/upload",
            files={"file": (file_path.name, f)},
            data={"name": "backup_name", "rows": 4}
        )
    assert response.status_code == 201
    
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
def jwt_bearer_mock(test_user):
    token_data = JWTDecodedData(
            sub=str(test_user.id),
            sid=123,
            exp=123,
            type=TokenType.BEARER
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
            type=TokenType.REFRESH
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