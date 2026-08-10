from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Body, Form, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from backend.schemas.jwt import JWTDecodedData
from backend.schemas.api_responses import BackupsResponse, MessageResponse
from backend.schemas.base import BackupData, SortByBackups
from backend.dependincies import get_db, verify_web_user
from backend.dao.backupDao import BackupDao
from backend.core.logger import get_logger
from backend.services.backup_service import delete_backup_by_path


logger = get_logger(__name__)

web_passwords = APIRouter()


#Ручка чтобы создать персональный файл с шифрованием

# + добавить функцию чтобы проверять создан ли файл у пользвоателя 
# (функция должна быть где-то в services или в dependencies)




# @web_passwords.post('/add')
# async def add_router(
#     token_data: JWTDecodedData = Depends()
# )