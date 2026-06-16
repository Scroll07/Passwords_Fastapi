import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_delete_wrong_backup_id(client: AsyncClient, jwt_bearer_mock, test_user):
    wrong_backup_id = 10
    response = await client.delete(
        url=f"/api/backups/{wrong_backup_id}",
    )

    assert response.status_code == 404
