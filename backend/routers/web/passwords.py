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


@web_passwords.post('/vaults/{vault_id}/passwords/add')
async def add__router(
    vault_id: int,
    password_data: PasswordDataRequest,
    token_data: JWTDecodedData = Depends(verify_web_user),
    vault_data: RequstVaultDependecie = Depends(web__check_vault_exists),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_data.sub)
    
    password_tool = PasswordTool(
        user_id=user_id,
        vault_id=vault_id,
        master_password=vault_data.master_password,
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
    label: str = Body(min_length=1),
    get_all: bool = Body(default=False),
    token_data: JWTDecodedData = Depends(verify_web_user),
    vault_data: RequstVaultDependecie = Depends(web__check_vault_exists),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_data.sub)
    
    password_tool = PasswordTool(
        user_id=user_id,
        vault_id=vault_id,
        master_password=vault_data.master_password,
        session=db
    )
    
    result = await password_tool.get_command(service=label, get_all=get_all)
    
    return {
        "ok": True,
        "passwords": result, #list[Password]
    }
