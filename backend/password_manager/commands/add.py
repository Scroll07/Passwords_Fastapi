import secrets

from backend.password_manager.services.file_utils import (
    load_data,
    save_data
)
from backend.password_manager.schemas.users import UserData
from backend.password_manager.schemas.passwords import Password


def add_command(
    user_data: UserData,
    service: str,
    username: str,
    password: str = "",
    note: str = "",
):
    if not password:
        password = secrets.token_urlsafe(24)
     
    data = load_data(user_data=user_data)
    
    labels = set(b.service for b in data.user_passwords)
    candidate = service
    i = 1
    while candidate in labels:
        candidate = service + '-' + str(i)
    
    password_to_add = Password(
        service=candidate,
        username=username,
        password=password,
        note=note
    )
    data.user_passwords.append(password_to_add)
    
    save_data(user_data=user_data, vault_data=data)