
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.session_dao import SessionDao
from src.services.jwt_service import JWT_Service, create_token_and_session
from src.dao.backupDao import BackupDao
from src.dao.role_dao import RoleDAO
from src.schemas.jwt import JWTDecodedData, TokenType
from src.schemas.db_schema import UserFields, UserRoles, CreateUserInDb
from src.schemas.api_responses import LoginResponse, MessageResponse, RefreshResponse
from src.dependincies import get_db, verify_refresh_token, get_jwt_service, verify_user, validate_change_passwords
from src.schemas.base import ChangePasswordSchema, RegisterRequestData, LoginRequest
from src.dao.userDao import UserDao
from src.core.logger import get_logger

logger = get_logger(__name__)

api_statistic = APIRouter()

@api_statistic.get("/backups/stats")
async def get_backup_stats(
    db: AsyncSession = Depends(get_db),
    data: JWTDecodedData = Depends(verify_user)
):
    try:
        dao = BackupDao(session=db)
        stats = await dao.stats__get_user_stats(user_id=int(data.sub))
        
        return {
            "ok": True,
            "stats": {
                "backups_count": stats.backups_count,
                "max_rows": stats.max_rows,
                "min_rows": stats.min_rows,
                "avg_rows": stats.avg_rows,
                "backups_for_week": stats.backups_for_week
            }
        }
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal Server Error")