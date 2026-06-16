import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
import pytest

import src.dao.backupDao as dao_file


@pytest.mark.asyncio
async def test_backups(client: AsyncClient, jwt_bearer_mock, test_user, tmp_path: Path, monkeypatch):
    file_path = tmp_path / "test_backup.json"
    file_path.write_bytes(b"My backup data")

    monkeypatch.setattr(dao_file, "BACKUPS", tmp_path)

    requests_to_create = 3
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

    response = await client.get(url="/api/backups")
    data = response.json()

    assert response.status_code == 200
    assert len(data.get("backups")) == requests_to_create
