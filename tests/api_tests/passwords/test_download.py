import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_download_wrong_backup_id(client: AsyncClient, jwt_bearer_mock, test_user):
    response = await client.post(
        url="/api/backups/download",
        json={"backup_id": 1000}
    )

    assert response.status_code == 404
