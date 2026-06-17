import pytest
from httpx import AsyncClient



@pytest.mark.asyncio
async def test_backups(client: AsyncClient, jwt_bearer_mock, test_user, create_one_backup):
    requests_to_create = 4
    for _ in range(requests_to_create):
        await create_one_backup()

    response = await client.get(url="/api/backups")
    data = response.json()

    assert response.status_code == 200
    assert len(data.get("backups")) == requests_to_create


@pytest.mark.asyncio
async def test_backups_without_backups(client: AsyncClient, jwt_bearer_mock, test_user):
    response = await client.get(
        url="/api/backups"
    )
    data = response.json()

    assert response.status_code == 200
    assert data.get("backups") == []
