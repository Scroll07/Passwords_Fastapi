import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


from src.schemas.base import RegisterRequestData, LoginRequest
from src.services.jwt_service import create_token_and_session
from src.schemas.jwt import TokenType

@pytest.mark.asyncio
async def test_register(client: AsyncClient):

    data = RegisterRequestData(
        username="test_user", password="pass", telegram_id=1910592094
    )

    response = await client.post(url="/api/register", json=data.model_dump())

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):

    user = RegisterRequestData(username="user", password="pass", telegram_id=1910592094)

    await client.post(url="/api/register", json=user.model_dump())

    response = await client.post(url="/api/register", json=user.model_dump())

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
    refresh_token = data.get("refresh_token")
    
    print(data)
    
    assert response.status_code == 200
    assert bearer_token is not None
    assert refresh_token is not None
    

@pytest.mark.asyncio
async def test_refresh_wrong_token(client: AsyncClient):
    response = await client.get(url="/api/refresh") # Response without headers and refresh token
    
    assert response.status_code == 401
    
    headers = {"Refresh": "wrong.token.actually"}
    response = await client.get(url="/api/refresh", headers=headers) # Response with wrong refresh token
    
    assert response.status_code == 401
    
@pytest.mark.asyncio
async def test_protected_router_without_token(client: AsyncClient):
    response = await client.get(url="/api/backups") # Response without headers and bearer token
    
    assert response.status_code == 401
    
    headers = {"Access": "Bearer wrong.token.actually"}
    response = await client.get(url="/api/refresh", headers=headers) # Response with wrong refresh token
    
    assert response.status_code == 401
    
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id, username, password, telegram_id, expected_code",
    [
        ("Short Username", "Max", "password", "1910592094", 422),
        ("Long username", "MaxMaxMaxMaxMaxMaxMaxMax", "password", "1910592094", 422),
        ("Username with space", "Max and Mia", "password", "1910592094", 422),
        ("Ok Username", "Maxim", "password", "1910592094", 201),
        ("Short passwrod", "Maxim", "pas", "1910592094", 422),
        ("Long passwrod", "Maxim", "passwordpasswordpassword", "1910592094", 422),
        ("Password with space", "Maxim", "password and pas", "1910592094", 422),
        ("Ok passwrod", "Maxim", "pass", "1910592094", 201),
        ("Short telegram id", "Maxim", "pass", "1000", 422),
        ("Long telegram id", "Maxim", "pass", "19105920940192383829238", 422),
        ("Ok telegram id", "Maxim", "pass", "1910592094", 201),
        
    ]
)
async def test_register_and_login_validation(
    id: str,
    username: str,
    password: str,
    telegram_id: int,
    expected_code: int,
    client: AsyncClient
):
    data = {
        "username": username,
        "password": password,
        "telegram_id": telegram_id
    }
    response = await client.post(
        url="/api/register",
        json=data
    )
    
    print(response.json())
    assert response.status_code == expected_code