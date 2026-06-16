import pytest
from httpx import AsyncClient


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
async def test_register_validation(
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

    assert response.status_code == expected_code
