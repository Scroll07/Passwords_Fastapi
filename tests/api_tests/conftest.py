import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


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