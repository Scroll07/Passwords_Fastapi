import pytest
from httpx import AsyncClient

from src.schemas.base import RegisterRequestData, LoginRequest
from src.dependincies import get_jwt_service

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

    # print(f"STATUS_CODE: {response.status_code}")
    assert response.status_code == 409
    

@pytest.mark.asyncio
async def test_login_ok(client: AsyncClient):
    username = "user"
    password = "pass"
    user = RegisterRequestData(
        username=username, 
        password=password, 
        telegram_id=1910592094
    )

    response = await client.post(url="/register", json=user.model_dump())

    assert response.status_code == 201

    login_data = LoginRequest(
        username=username,
        password=password
    )
    
    response = await client.post(url="/login", json=login_data.model_dump())
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

    response = await client.post(url="/register", json=user.model_dump())

    assert response.status_code == 201

    login_data = LoginRequest(
        username=username,
        password="wrong password"
    )
    
    response = await client.post(url="/login", json=login_data.model_dump())
    
    assert response.status_code == 401
    
@pytest.mark.asyncio
async def test_refresh(client: AsyncClient):
    jwt_service = get_jwt_service()
    refresh_token = jwt_service.create_refresh_token(user_id=123)
    headers = {"Refresh": refresh_token.token}
    
    response = await client.get(url="/refresh", headers=headers)
    
    data = response.json()
    bearer_token = data.get("bearer_token")
    refresh_token = data.get("refresh_token")
    
    assert response.status_code == 200
    assert bearer_token is not None
    assert refresh_token is not None
    

@pytest.mark.asyncio
async def test_refresh_wrong_token(client: AsyncClient):
    response = await client.get(url="/refresh") # Response without headers and refresh token
    
    assert response.status_code == 401
    
    # headers = {"Refresh": "wrong.token.actually"}
    # response = await client.get(url="/refresh", headers=headers) # Response with wrong refresh token
    
    # assert response.status_code == 401
    
@pytest.mark.asyncio
async def test_protected_router_without_token(client: AsyncClient):
    response = await client.get(url="/backups") # Response without headers and bearer token
    
    assert response.status_code == 401
    
    # headers = {"Access": "Bearer wrong.token.actually"}
    # response = await client.get(url="/refresh", headers=headers) # Response with wrong refresh token
    
    # assert response.status_code == 401
    
