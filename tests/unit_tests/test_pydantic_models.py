import pytest
from pydantic import ValidationError

from backend.schemas.base import RegisterRequestData, LoginRequest, CreateVaultData


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

def test_CreateVaultData__ok():
    data = CreateVaultData(
        name="Usual name",
        master_password="usual_password"
    )
    assert data.name == "Usual name"
    assert data.master_password == "usual_password"


def test_CreateVaultData__no_name__raises():
    with pytest.raises(ValidationError):
        data = CreateVaultData(
            name="",
            master_password="usual_password"
        )

def test_CreateVaultData__long_name__raises():
    with pytest.raises(ValidationError):
        data = CreateVaultData(
            name="Looooooooooooooooooooooooooong Name",
            master_password="usual_password"
        )

def test_CreateVaultData__long_password__raises():
    with pytest.raises(ValidationError):
        data = CreateVaultData(
            name="Name",
            master_password="Looooooooooooooooooooooooooong_password"
        )

def test_CreateVaultData__password_with_space__raises():
    with pytest.raises(ValidationError):
        data = CreateVaultData(
            name="Name",
            master_password="Master password"
        )
        
def test_CreateVaultData__startwith_spaces__ok():
    data = CreateVaultData(
        name="   Name  ",
        master_password="  password  "
    )
    assert data.name == "Name"
    assert data.master_password == "password"
    
    

