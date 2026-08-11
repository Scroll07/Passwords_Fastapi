
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dao.backupDao import BackupDao
from backend.schemas.jwt import JWTDecodedData
from backend.dependencies import get_db
from backend.api_dependencies import verify_user
from backend.core.logger import get_logger

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