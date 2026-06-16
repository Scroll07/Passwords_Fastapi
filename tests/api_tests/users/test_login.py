import pytest
from httpx import AsyncClient

from src.schemas.base import RegisterRequestData, LoginRequest


@pytest.mark.asyncio
async def test_login_ok(client: AsyncClient):
    username = "user"
    password = "pass"
    user = RegisterRequestData(
        username=username,
        password=password,
        telegram_id=1910592094
    )

    response = await client.post(url="/api/register", json=user.model_dump())
    assert response.status_code == 201

    login_data = LoginRequest(
        username=username,
        password=password
    )

    response = await client.post(url="/api/login", json=login_data.model_dump())
    data = response.json()
    bearer_token = data.get("bearer_token")
    refresh_token = data.get("refresh_token")

    assert response.status_code == 200
    assert bearer_token is not None
    assert refresh_token is not None


@pytest.mark.asyncio
async def test_login_wrong_creds(client: AsyncClient):
    username = "user"
    password = "pass"
    user = RegisterRequestData(
        username=username,
        password=password,
        telegram_id=1910592094
    )

    response = await client.post(url="/api/register", json=user.model_dump())
    assert response.status_code == 201

    login_data = LoginRequest(
        username=username,
        password="wrong_password"
    )

    response = await client.post(url="/api/login", json=login_data.model_dump())

    assert response.status_code == 401
