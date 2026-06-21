import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
import pytest

import src.dao.backupDao as dao_file
from src.dao.backupDao import BackupDao


@pytest.mark.asyncio
async def test_delete_backup__ok(client: AsyncClient, jwt_bearer_mock, db_session: AsyncSession, test_user, test_backup):
    user_id = test_user.id
    backup_id = 1
    dao = BackupDao(session=db_session)
    backup = await dao.get_backup_by_id(backup_id=backup_id, user_id=user_id)

    assert backup is not None

    response = await client.delete(
        url=f"/api/backups/{backup.id}",
    )

    assert response.status_code == 200
    assert not Path(backup.path).exists()

    backup = await dao.get_backup_by_id(backup_id=backup_id, user_id=user_id)
    assert backup is None


@pytest.mark.asyncio
async def test_delete_backup__wrong_id__returns_not_found(client: AsyncClient, jwt_bearer_mock, test_user):
    wrong_backup_id = 10
    response = await client.delete(
        url=f"/api/backups/{wrong_backup_id}",
    )

    assert response.status_code == 404
