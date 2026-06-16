import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_backups_without_backups(client: AsyncClient, jwt_bearer_mock, test_user):
    response = await client.get(
        url="/api/backups"
    )
    data = response.json()

    assert response.status_code == 200
    assert data.get("backups") == []
