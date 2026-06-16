import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
import pytest

import src.dao.backupDao as dao_file
from src.dao.backupDao import BackupDao


@pytest.mark.asyncio
async def test_delete(client: AsyncClient, jwt_bearer_mock, tmp_path: Path, monkeypatch, db_session: AsyncSession, test_user):
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
