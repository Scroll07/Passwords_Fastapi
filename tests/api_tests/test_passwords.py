import asyncio
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
        
@pytest.mark.asyncio
async def test_backups_without_backups(client: AsyncClient, jwt_bearer_mock: int, create_test_user):
    response = await client.get(
        url="/backups"
    )
    data = response.json()

    assert response.status_code == 200
    assert data.get("backups") == []

@pytest.mark.asyncio
async def test_backups(client: AsyncClient, jwt_bearer_mock: int, create_test_user, tmp_path: Path, monkeypatch):
    
    #create file    
    file_path = tmp_path / "test_backup.json"
    file_path.write_bytes(b"My backup data")
    
    monkeypatch.setattr(dao_file, "BACKUPS", tmp_path)
    
    #requests for creating backups
    requests_to_create = 3
    with open(file_path, "rb") as f:
        tasks = [client.post(
            url="/backups/upload",
            files={"file": (file_path.name, f)},
            data={"name": "backup_name", "rows": 4}
        )
        for _ in range(requests_to_create)]
        responses = await asyncio.gather(*tasks)
        for r in responses:
            assert r.status_code == 200
        
    # /backups request
    response = await client.get(
        url="/backups"
    )
    data = response.json()
    
    assert response.status_code == 200
    assert len(data.get("backups")) == requests_to_create
        


@pytest.mark.asyncio
async def test_download_wrong_backup_id(client: AsyncClient, jwt_bearer_mock: int, create_test_user):
    response = await client.post(
        url="/backups/download",
        json={"backup_id": 1000}
    )

    assert response.status_code == 404
    
@pytest.mark.asyncio
async def test_download_no_backup_file_on_server(client: AsyncClient, jwt_bearer_mock: int, create_test_user, tmp_path: Path, monkeypatch, db_session: AsyncSession):
    #create file    
    file_path = tmp_path / "test_backup.json"
    file_path.write_bytes(b"My backup data")
    
    monkeypatch.setattr(dao_file, "BACKUPS", tmp_path)
    
    #requests for creating backups
    requests_to_create = 1
    with open(file_path, "rb") as f:
        tasks = [client.post(
            url="/backups/upload",
            files={"file": (file_path.name, f)},
            data={"name": "backup_name", "rows": 4}
        )
        for _ in range(requests_to_create)]
        responses = await asyncio.gather(*tasks)
        for r in responses:
            assert r.status_code == 200
            
    #delete backup
    user_id = jwt_bearer_mock
    dao = BackupDao(session=db_session)
    backups = await dao.get_user_backups(user_id=user_id)
    for b in backups:
        Path(b.path).unlink()
    
    response = await client.post(
        url="/backups/download",
        json={"backup_id": 1}
    )
    data = response.json()
    
    assert response.status_code == 500
    assert data.get("message") == "We cant find your backup"
    
    
@pytest.mark.asyncio
async def test_download(client: AsyncClient, jwt_bearer_mock: int, create_test_user, tmp_path: Path, monkeypatch):
    #create file    
    file_path = tmp_path / "test_backup.json"
    backup_data = b"My backup data"
    file_path.write_bytes(backup_data)
    
    monkeypatch.setattr(dao_file, "BACKUPS", tmp_path)
    
    #requests for creating backups
    requests_to_create = 1
    with open(file_path, "rb") as f:
        tasks = [client.post(
            url="/backups/upload",
            files={"file": (file_path.name, f)},
            data={"name": "backup_name", "rows": 4}
        )
        for _ in range(requests_to_create)]
        responses = await asyncio.gather(*tasks)
        for r in responses:
            assert r.status_code == 200
    
    response = await client.post(
        url="/backups/download",
        json={"backup_id": 1}
    )
    
    assert response.status_code == 200
    assert response.content ==  backup_data

    
@pytest.mark.asyncio
async def test_delte_wrong_backup_id(client: AsyncClient, jwt_bearer_mock: int, create_test_user):
    wrong_backup_id = 10
    response = await client.delete(
        url=f"/backups/{wrong_backup_id}",
    )
    
    assert response.status_code == 404
    

@pytest.mark.asyncio
async def test_delete(client: AsyncClient, jwt_bearer_mock: int, create_test_user, tmp_path: Path, monkeypatch, db_session: AsyncSession):
    #create file    
    file_path = tmp_path / "test_backup.json"
    backup_data = b"My backup data"
    file_path.write_bytes(backup_data)
    
    monkeypatch.setattr(dao_file, "BACKUPS", tmp_path)
    
    #requests for creating backups
    requests_to_create = 1
    with open(file_path, "rb") as f:
        tasks = [client.post(
            url="/backups/upload",
            files={"file": (file_path.name, f)},
            data={"name": "backup_name", "rows": 4}
        )
        for _ in range(requests_to_create)]
        responses = await asyncio.gather(*tasks)
        for r in responses:
            assert r.status_code == 200
    
    
    user_id = jwt_bearer_mock
    backup_id = 1
    dao = BackupDao(session=db_session)
    backup = await dao.get_backup_by_id(backup_id=backup_id, user_id=user_id)
    
    assert backup is not None
        
    response = await client.delete(
        url=f"/backups/{backup.id}",
    )

    assert response.status_code == 200
    assert not Path(backup.path).exists()

    backup = await dao.get_backup_by_id(backup_id=backup_id, user_id=user_id)
    assert backup is None