import pytest
from pydantic import ValidationError

from src.schemas.base import RegisterRequestData, LoginRequest


def test_LoginRequest__ok():
    data = LoginRequest(
        username="user",
        password="password"
    )
    assert data.username == "user"
    assert data.password == "password"
    
def test_LoginRequest__username_with_space__raises():
    with pytest.raises(ValidationError):
        data = LoginRequest(
            username="name with spaces",
            password="password"
        )
        
def test_LoginRequest__username_too_short__raises():
    with pytest.raises(ValidationError):
        data = LoginRequest(
            username="Max",
            password="password"
        )
        
def test_LoginRequest__password_too_long__raises():
    with pytest.raises(ValidationError):
        data = LoginRequest(
            username="user",
            password="long______________________________password"
        )
    

def test_RegisterRequestData__valid_telegram_id():
    data = RegisterRequestData(
        username="user",
        password="password",
        telegram_id=199999999
    )
    assert data.telegram_id == 199999999
    
def test_RegisterRequestData__telegram_id_too_short__raises():
    with pytest.raises(ValidationError):
        data = RegisterRequestData(
            username="user",
            password="password",
            telegram_id=10
        )

def test_RegisterRequestData__telegram_id_too_long__raises():
    with pytest.raises(ValidationError):
        data = RegisterRequestData(
            username="user",
            password="password",
            telegram_id=10000000000000000000000000000000
        )
        

        

