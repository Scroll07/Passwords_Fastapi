import pytest
from httpx import AsyncClient

from src.schemas.base import RegisterRequestData


@pytest.mark.asyncio
async def test_register(client: AsyncClient):

    data = RegisterRequestData(
        username="test_user", password="pass", telegram_id=1910592094
    )

    response = await client.post(url="/register", json=data.model_dump())

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):

    user = RegisterRequestData(username="user", password="pass", telegram_id=1910592094)

    await client.post(url="/register", json=user.model_dump())

    response = await client.post(url="/register", json=user.model_dump())

    print(f"STATUS_CODE: {response.status_code}")
    assert response.status_code == 409
