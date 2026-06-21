import pytest
from httpx import AsyncClient

from src.schemas.base import RegisterRequestData, LoginRequest


@pytest.mark.asyncio
async def test_successfull_logout(client: AsyncClient, register_test_user: RegisterRequestData):
    #LOGIN
    data = LoginRequest(
        username=register_test_user.username,
        password=register_test_user.password
    )
    response = await client.post(
        url="/api/login",
        json=data.model_dump()
    )
    assert response.status_code == 200
    json_data = response.json()
    bearer_token = json_data.get("bearer_token").get("token")
    assert bearer_token is not None
        
    #LOGOUT
    response = await client.post(
        url="/api/logout",
        headers={"Authorization": f"Bearer {bearer_token}"}
    )
    assert response.status_code == 200
    
    #Second Logout
    response = await client.post(
        url="/api/logout",
        headers={"Authorization": f"Bearer {bearer_token}"}
    )
    
    assert response.status_code == 401
    
    