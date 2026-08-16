from datetime import datetime
from fastapi import APIRouter, Body, Form, UploadFile, File, Depends, HTTPException, Query
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dao.userDao import UserDao

from backend.schemas.jwt import JWTDecodedData
from backend.schemas.base import VaultInfo
from backend.dependencies import get_db
from backend.web_dependencies import verify_web_user, web__check_vault_exists
from backend.core.logger import get_logger
from backend.services.backup_service import delete_backup_by_path
from backend.schemas.requests import RequstVaultDependecie
from backend.dao.vaultDao import VaultDao, VaultFields
from backend.services.secrets import (
    hash_password,
    verify_password
)

from backend.password_manager.services.password import (
    create_user_vault,
    check_is_vault_exists
)
from backend.password_manager.schemas.passwords import PasswordDataRequest
from backend.password_manager.schemas.users import UserData
from backend.password_manager.core.password_tool import PasswordTool



logger = get_logger(__name__)

web_passwords = APIRouter()


#Ручка чтобы создать персональный файл с шифрованием

# + добавить функцию чтобы проверять создан ли файл у пользвоателя 
# (функция должна быть где-то в services или в dependencies)

# Добавь логи к каждой ручке

@web_passwords.post('/create-vault')
async def create_vault__router(
    vault_name: str = Body(),
    vault_master_password: str = Body(),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        # Получить информацию пользователя (username  и т.д.)
        user_id = int(token_data.sub)
        dao = UserDao(session=db)
        user_data = await dao.get_user_data(user_id=user_id)
        if not user_data:
            raise HTTPException(404, "Wrong user data")
        
        # Проверить существует ли `vault`
        vault_name = vault_name.strip()
        is_vault_exists = check_is_vault_exists(username=user_data.username, vault_name=vault_name)
        if is_vault_exists:
            raise HTTPException(409, "Vault with such name alredy exists")
        
        # Провалидировать данные
        vault_data = VaultInfo(
            name=vault_name,
            master_password=vault_master_password
        )
        
        # Создать Vault
        encrypted_data = create_user_vault(master_password=vault_master_password)  # encrypted_passwords: str encrypted_dek: bytes
        
        # Сохранить данные в бд
        vault_dao = VaultDao(session=db)
        await vault_dao.create_vault(
            user_id=user_id,
            name=vault_name,
            encrypted_passwords=encrypted_data.encrypted_passwords,
            salt=encrypted_data.salt,
            encrypted_dek=encrypted_data.encrypted_dek
        )
        
        return {
            "ok": True,
            "detail": "New vault was successfully created"
        }
        
    except HTTPException as e:
        raise e
    except ValidationError as e:
        raise HTTPException(401, e.errors)
    except Exception as e:
        raise HTTPException(500, 'Internal server error')



@web_passwords.post('/add')
async def add__router(
    password_data: PasswordDataRequest,
    token_and_vault_data: RequstVaultDependecie = Depends(web__check_vault_exists),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_and_vault_data.token_data.sub)
    
    password_tool = PasswordTool(
        user_id=user_id,
        vault_id=token_and_vault_data.vault.id,
        master_password=token_and_vault_data.master_password,
        session=db
    )
    pas_data = password_data.pas_data
    await password_tool.add_command(
        service=pas_data.service,
        username=pas_data.username,
        password=pas_data.password,
        note=pas_data.note
    )
    
    return {
        "ok": True,
        "detail": "New password entry was created"
    }
    
    # Добавить обработку ошибок, включительно ValueError
    # Добавить логирование
    
@web_passwords.post('/get')
async def get__router(
    label: str = Body(min_length=1),
    token_and_vault_data: RequstVaultDependecie = Depends(web__check_vault_exists),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_and_vault_data.token_data.sub)
    
    password_tool = PasswordTool(
        user_id=user_id,
        vault_id=token_and_vault_data.vault.id,
        master_password=token_and_vault_data.master_password,
        session=db
    )
    
    
    return {
        "ok": True,
        "detail": "New password entry was created"
    }
