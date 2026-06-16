from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.backupDao import BackupDao
from tests.api_tests.conftest import test_backup


@pytest.mark.asyncio
async def test_upload(client: AsyncClient, jwt_bearer_mock, test_user, db_session: AsyncSession):
    requests_to_create = 4
    for _ in range(requests_to_create):
        await test_backup() # type: ignore


    user_id = test_user.id

    dao = BackupDao(session=db_session)
    backups = await dao.get_user_backups(user_id=user_id)

    assert backups != []

    for backup in backups:
        assert Path(backup.path).exists() and Path(backup.path).is_file()


@pytest.mark.asyncio
async def test_upload_without_file(client: AsyncClient, jwt_bearer_mock):
    data = {"name": "backup_name", "rows": 4}
    response = await client.post(
        url="/api/backups/upload",
        data=data
    )

    assert response.status_code == 422
