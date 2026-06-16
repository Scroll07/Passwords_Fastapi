import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.jwt_service import create_token_and_session
from src.schemas.jwt import TokenType


@pytest.mark.asyncio
async def test_refresh(client: AsyncClient, db_session: AsyncSession, test_user, jwt_service):
    refresh_token = await create_token_and_session(
        session=db_session,
        jwt_service=jwt_service,
        user_id=test_user.id,
        token_type=TokenType.REFRESH
    )
    await db_session.commit()

    headers = {"Refresh": refresh_token.token}

    response = await client.get(url="/api/refresh", headers=headers)

    data = response.json()
    bearer_token = data.get("bearer_token")
    new_refresh_token = data.get("refresh_token")

    assert response.status_code == 200
    assert bearer_token is not None
    assert new_refresh_token is not None


@pytest.mark.asyncio
async def test_refresh_wrong_token(client: AsyncClient):
    response = await client.get(url="/api/refresh")
    assert response.status_code == 401

    headers = {"Refresh": "wrong.token.actually"}
    response = await client.get(url="/api/refresh", headers=headers)
    assert response.status_code == 401
