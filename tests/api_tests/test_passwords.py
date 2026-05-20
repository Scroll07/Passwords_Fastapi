from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
import pytest


import src.dao.backupDao as dao_file
from src.dao.backupDao import BackupDao



@pytest.mark.asyncio
async def test_upload_without_file(client: AsyncClient, jwt_bearer_mock):
    data = {"name": "backup_name", "rows": 4}
    response = await client.post(
        url="/backups/upload",
        # files=[], #No files
        data=data
    )
    
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_upload(client: AsyncClient, jwt_bearer_mock, create_test_user, db_session: AsyncSession, tmp_path: Path, monkeypatch):
    #create file
    user_id = jwt_bearer_mock
    
    file_path = tmp_path / "test_backup.json"
    file_path.write_bytes(b"My backup data")
    
    monkeypatch.setattr(dao_file, "BACKUPS", tmp_path) # Замена папки сохранения бэкапа на временную
    
    #request
    with open(file_path, "rb") as f:
        data = {"name": "backup_name", "rows": 4}
        response = await client.post(
            url="backups/upload",
            files={"file": (file_path.name, f)},
            data=data
        )
    
    dao = BackupDao(session=db_session)
    backups = await dao.get_user_backups(user_id=user_id)
    
    
    assert response.status_code == 200    
    assert backups != []

    for backup in backups:
        assert Path(backup.path).exists() and Path(backup.path).is_file()







