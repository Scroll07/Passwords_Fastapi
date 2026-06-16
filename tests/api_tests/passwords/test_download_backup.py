import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
import pytest

from src.dao.backupDao import BackupDao


@pytest.mark.asyncio
async def test_download_no_backup_file_on_server(
    client: AsyncClient, jwt_bearer_mock, tmp_path: Path, monkeypatch,
    db_session: AsyncSession, test_user, test_backup
):

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
    backup_data = b"My backup data"

    response = await client.post(
        url="/api/backups/download",
        json={"backup_id": 1}
    )

    assert response.status_code == 200
    assert response.content == backup_data


@pytest.mark.asyncio
async def test_download_wrong_backup_id(client: AsyncClient, jwt_bearer_mock, test_user):
    response = await client.post(
        url="/api/backups/download",
        json={"backup_id": 1000}
    )

    assert response.status_code == 404
