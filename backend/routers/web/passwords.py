from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Body, Form, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from backend.dao.userDao import UserDao

from backend.schemas.jwt import JWTDecodedData
from backend.schemas.api_responses import BackupsResponse, MessageResponse
from backend.schemas.base import BackupData, SortByBackups
from backend.dependincies import get_db, verify_web_user
from backend.dao.backupDao import BackupDao
from backend.core.logger import get_logger
from backend.services.backup_service import delete_backup_by_path

from backend.password_manager.services.password import (
    create_user_vault,
    check_is_vault_exists
)
from backend.password_manager.schemas.passwords import PasswordDataRequest

logger = get_logger(__name__)

web_passwords = APIRouter()


#Ручка чтобы создать персональный файл с шифрованием

# + добавить функцию чтобы проверять создан ли файл у пользвоателя 
# (функция должна быть где-то в services или в dependencies)


@web_passwords.post('/create-vault')
async def create_vault__router(
    vault_name: str = Body(gt=0, lt=17),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
):
    # Получить информациб пользователя (username  и т.д.)
    user_id = int(token_data.sub)
    dao = UserDao(session=db)
    user_data = await dao.get_user_data(user_id=user_id)
    if not user_data:
        raise HTTPException(404, "User with such was not found")
    
    # Проверить существует ли `vault`
    vault_name = vault_name.strip()
    is_vault_exists = check_is_vault_exists(username=user_data.username, vault_name=vault_name)
    if is_vault_exists:
        raise HTTPException(409, "Vault with such name alredy exists")
    
    create_user_vault(username=user_data.username, vault_name=vault_name)
    
    return {
        "ok": True,
        "detail": "New vault was successfully created"
    }




@web_passwords.post('/add')
async def add__router(
    password_data: PasswordDataRequest,
    token_data: JWTDecodedData = Depends(),
    db: AsyncSession = Depends(get_db),
):
    