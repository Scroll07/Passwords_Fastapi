import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
import pytest

import src.dao.backupDao as dao_file
from src.dao.backupDao import BackupDao


@pytest.mark.asyncio
async def test_download_no_backup_file_on_server(
    client: AsyncClient, jwt_bearer_mock, tmp_path: Path, monkeypatch,
    db_session: AsyncSession, test_user
):
    file_path = tmp_path / "test_backup.json"
    file_path.write_bytes(b"My backup data")

    monkeypatch.setattr(dao_file, "BACKUPS", tmp_path)

    requests_to_create = 1
    with open(file_path, "rb") as f:
        tasks = [client.post(
            url="/api/backups/upload",
            files={"file": (file_path.name, f)},
            data={"name": "backup_name", "rows": 4}
        )
        for _ in range(requests_to_create)]
        responses = await asyncio.gather(*tasks)
        for r in responses:
            assert r.status_code == 200

    user_id = test_user.id
    dao = BackupDao(session=db_session)
    backups = await dao.get_user_backups(user_id=user_id)
    for b in backups:
        Path(b.path).unlink()

    response = await client.post(
        url="/api/backups/download",
        json={"backup_id": 1}
    )
    data = response.json()

    assert response.status_code == 500
    assert data.get("detail") == "We cant find your backup"


@pytest.mark.asyncio
async def test_download(client: AsyncClient, jwt_bearer_mock, tmp_path: Path, monkeypatch):
    file_path = tmp_path / "test_backup.json"
    backup_data = b"My backup data"
    file_path.write_bytes(backup_data)

    monkeypatch.setattr(dao_file, "BACKUPS", tmp_path)

    requests_to_create = 1
    with open(file_path, "rb") as f:
        tasks = [client.post(
            url="/api/backups/upload",
            files={"file": (file_path.name, f)},
            data={"name": "backup_name", "rows": 4}
        )
        for _ in range(requests_to_create)]
        responses = await asyncio.gather(*tasks)
        for r in responses:
            assert r.status_code == 200

    response = await client.post(
        url="/api/backups/download",
        json={"backup_id": 1}
    )

    assert response.status_code == 200
    assert response.content == backup_data
