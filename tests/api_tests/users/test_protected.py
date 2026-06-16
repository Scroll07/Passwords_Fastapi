import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_protected_router_without_token(client: AsyncClient):
    response = await client.get(url="/api/backups")
    assert response.status_code == 401

    headers = {"Access": "Bearer wrong.token.actually"}
    response = await client.get(url="/api/backups", headers=headers)
    assert response.status_code == 401
