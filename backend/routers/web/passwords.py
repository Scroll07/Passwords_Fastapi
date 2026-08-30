from datetime import datetime
from fastapi import APIRouter, Body, Form, UploadFile, File, Depends, HTTPException, Query
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dao.userDao import UserDao

from backend.schemas.jwt import JWTDecodedData
from backend.dependencies import get_db
from backend.web_dependencies import verify_vault_session, verify_web_user
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
from backend.password_manager.schemas.passwords import Password


logger = get_logger(__name__)

web_passwords = APIRouter()


@web_passwords.post('/vaults/{vault_id}/passwords/add')
async def add__router(
    vault_id: int,
    password_data: PasswordDataRequest,
    vault_data: RequstVaultDependecie = Depends(verify_vault_session),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_data.sub)
    
    password_tool = PasswordTool(
        user_id=user_id,
        vault=vault_data.vault,
        dek=vault_data.dek,
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
    
    
@web_passwords.post('/vaults/{vault_id}/passwords/get')
async def get__router(
    vault_id: int,
    service: str = Body(default=''),
    get_all: bool = Body(default=False),
    vault_data: RequstVaultDependecie = Depends(verify_vault_session),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_data.sub)
    
    password_tool = PasswordTool(
        user_id=user_id,
        vault=vault_data.vault,
        dek=vault_data.dek,
        session=db
    )
    
    service = service.strip()
    if len(service) < 1 and not get_all:
        raise HTTPException(401, "Request must include service name or get_all parameter")
    
    result = await password_tool.get_command(service=service, get_all=get_all)
    
    return {
        "ok": True,
        "passwords": result, #list[Password]
    }
    # Добавить обработку ошибок, включительно ValueError
    # Добавить логирование

@web_passwords.post('/vaults/{vault_id}/passwords/delete')
async def delete__router(
    vault_id: int,
    service: str = Body(min_length=1),
    delete_all: bool = Body(False),
    vault_data: RequstVaultDependecie = Depends(verify_vault_session),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_data.sub)
        
    password_tool = PasswordTool(
        user_id=user_id,
        vault=vault_data.vault,
        dek=vault_data.dek,
        session=db
    )
    
    await password_tool.delete_command(service=service, delete_all=delete_all)
    
    return {
        "ok": True,
        "detail": "Password was deleted"
    }
    # Добавить обработку ошибок, включительно ValueError
    # Добавить логирование
    
@web_passwords.post('/vaults/{vault_id}/passwords/update')
async def update__router(
    password_data: Password,
    vault_id: int,
    vault_data: RequstVaultDependecie = Depends(verify_vault_session),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_data.sub)
        
    password_tool = PasswordTool(
        user_id=user_id,
        vault=vault_data.vault,
        dek=vault_data.dek,
        session=db
    )
    
    await password_tool.edit_command(
        serivce=password_data.service,
        username=password_data.username,
        password=password_data.password,
        note=password_data.note
    )
    
    return {
        "ok": True,
        "detail": "Password data was updated"
    }
    # Добавить обработку ошибок, включительно ValueError
    # Добавить логирование
    
    