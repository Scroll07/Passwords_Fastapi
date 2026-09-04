from sqlalchemy.ext.asyncio import AsyncSession

from backend.password_manager.core.password_tool import PasswordTool
from backend.password_manager.core.crypto import (
    derive_key,
    decrypt_dek,
    decrypt_vault_passwords,
    encrypt_vault_passwords
)
from backend.dao.vaultDao import Vaults
from backend.password_manager.schemas.passwords import Password


MASTER_PASSWORD = 'Master Passowrd' 


async def test_add_command(password_tool: PasswordTool, db_vault: Vaults):
    await password_tool.add_command(
        service="service",
        username="username",
        password="password",
        note='note'
    )
    
    passwords = decrypt_vault_passwords(db_vault.encrypted_passwords, key=password_tool.dek)
    passwords = passwords.passwords
    assert len(passwords) == 1
    password = passwords[0]
    assert password.service == 'service'
    assert password.username == 'username'
    assert password.password == 'password'
    assert password.note == 'note'

async def test_get_command(password_tool: PasswordTool, db_vault: Vaults):
    await password_tool.add_command(
        service="service",
        username="username",
        password="password",
        note='note'
    )
    
    password = await password_tool.get_command(service='service', strict=True)
    assert type(password) == Password
    assert password.service == 'service'
    assert password.username == 'username'
    assert password.password == 'password'
    assert password.note == 'note'
    
    passwords = decrypt_vault_passwords(db_vault.encrypted_passwords, key=password_tool.dek)
    assert password == passwords.passwords[0]
    
    