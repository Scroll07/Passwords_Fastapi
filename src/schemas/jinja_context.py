from pydantic import BaseModel
from typing import Any

from src.schemas.base import BackupData 

class UserBackupContext(BaseModel):
    backup: BackupData | None = None
    success: str = ''
    error: str = ''


class _FormData(BaseModel):
    username: str
    password: str

class LoginRegisterContext(BaseModel):
    error: Any = ''
    form_data: _FormData