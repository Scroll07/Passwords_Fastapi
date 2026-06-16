import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_upload_without_file(client: AsyncClient, jwt_bearer_mock):
    data = {"name": "backup_name", "rows": 4}
    response = await client.post(
        url="/api/backups/upload",
        data=data
    )

    assert response.status_code == 422
