import pytest
from httpx import AsyncClient


from tests.api_tests.conftest import test_backup

@pytest.mark.asyncio
async def test_backups(client: AsyncClient, jwt_bearer_mock, test_user):
    requests_to_create = 4
    for _ in range(requests_to_create):
        await test_backup() # type: ignore

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
