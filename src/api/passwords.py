from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException, Body
from fastapi.responses import FileResponse

from src.schemas.base import BackupData, DownloadRequest, UploadRequest
from src.dependincies import get_db, verify_user
from src.dao.backupDao import BackupDao
from src.core.logger import get_logger
from src.services.backup_service import delete_backup_by_path

logger = get_logger(__name__)

passwords = APIRouter()


@passwords.post("/backups/upload")
async def upload_post(
    name: str = Form(...),
    rows: int = Form(...),
    file: UploadFile = File(...),
    db=Depends(get_db),
    user_id=Depends(verify_user),
):
    try:
        dao = BackupDao(db)
        if file.filename is None:
            raise HTTPException(401, detail="Filename is None")

        new_backup = dao.create_backup(user_id=user_id, filename=file.filename, name=name, rows=rows)
        async with new_backup as backup:
            content = await file.read()
            with open(backup.path, "wb") as f:
                f.write(content)

            return {"ok": True, "message": "Your backup was successfully uploaded"}
    except HTTPException as e:
        logger.warning(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")


@passwords.get("/backups")
async def get_user_backups(
    db = Depends(get_db),
    user_id = Depends(verify_user),
):
    try:
        dao = BackupDao(session=db)
        backups = await dao.get_user_backups(user_id=user_id)
        backups_data = [
            BackupData(
                id=b.id,
                created_at=b.created_at,
                name=b.name_to_show,
                rows=b.rows
            )
            for b in backups
        ]
        return {"ok": True, "message": f"Backups of {user_id}", "backups": backups_data}
    except Exception as e:
        logger.exception(f"Error in Backups handler: {e}")
        raise HTTPException(500, detail="Interal server error")
    

@passwords.post("/backups/download")
async def download_post(
   data: DownloadRequest, 
   db = Depends(get_db),
   user_id = Depends(verify_user),
):
    try:
        dao = BackupDao(session=db)
        backup = await dao.get_backup_by_id(backup_id=data.backup_id, user_id=user_id)
        if backup is None:
            raise HTTPException(404, "Backup was not found")
            
        if not Path(backup.path).exists():
            raise HTTPException(500, "We cant find your backup")
        
        now = datetime.now()
        date = datetime.strftime(now, format="%d-%m-%Y_%H-%M-%S")
        
        return FileResponse(
        path=backup.path,
        filename=f'backup_{date}.json',
        media_type="application/json"
        )
    except HTTPException as e:
        logger.exception(f"Error in Download handler: {e}")
        raise e
    except Exception as e:
        logger.exception(f"Error in Download handler: {e}")
        raise HTTPException(500, detail="Internal server error")
    

@passwords.delete("/backups/{backup_id}")
async def delete_backup(
   backup_id: int, 
   db = Depends(get_db),
   user_id = Depends(verify_user),
):
    dao = BackupDao(session=db)
    deleted_backup = await dao.delete_backup_by_id(backup_id=backup_id, user_id=user_id)
    if deleted_backup is None:
        raise HTTPException(404, detail=f"Backup with '{backup_id}' id was not found at your account")
    
    #delete file local
    delete_backup_by_path(backup_path=Path(deleted_backup.path))
    
    return {"ok": True, "message": "Your backup was successully deleted"}
    