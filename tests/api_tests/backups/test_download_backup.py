from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
import pytest

from backend.dao.backupDao import BackupDao


@pytest.mark.asyncio
async def test_download_backup__file_missing__returns_server_error(
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

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_download_backup__ok(client: AsyncClient, jwt_bearer_mock, test_backup):
    backup_data = b"My backup data"

    response = await client.post(
        url="/api/backups/download",
        json={"backup_id": test_backup.id}
    )

    assert response.status_code == 200
    assert response.content == backup_data


@pytest.mark.asyncio
async def test_download_backup__wrong_id__returns_not_found(client: AsyncClient, jwt_bearer_mock, test_user):
    response = await client.post(
        url="/api/backups/download",
        json={"backup_id": 1000}
    )

    assert response.status_code == 404
