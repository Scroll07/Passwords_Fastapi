from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Body, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse

from src.schemas.api_responses import BackupsResponse, MessageResponse
from src.schemas.base import BackupData, DownloadRequest
from src.dependincies import get_db, verify_user
from src.dao.backupDao import BackupDao
from src.core.logger import get_logger
from src.services.backup_service import delete_backup_by_path

logger = get_logger(__name__)

web_passwords = APIRouter()


#==============================
#            WEB    
#==============================
from src.dependincies import verify_web_user

@web_passwords.post("/backups/upload")
async def web_upload_post(
    name: str = Form(...),
    rows: int = Form(...),
    file: UploadFile = File(...),
    db=Depends(get_db),
    user_id=Depends(verify_web_user),
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

            response = MessageResponse(
                ok=True,
                detail="Your backup was successfully uploaded"
            )
            return response

    except HTTPException as e:
        logger.warning(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")


@web_passwords.get("/backups")
async def web_get_user_backups(
    db = Depends(get_db),
    user_id = Depends(verify_web_user),
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
        response = BackupsResponse(
            ok=True,
            detail=f"Backups of {user_id}",
            backups=backups_data
        )
        
        return response
    except Exception as e:
        logger.exception(f"Error in Backups handler: {e}")
        raise HTTPException(500, detail="Interal server error")
    

@web_passwords.post("/backups/download")
async def web_download_post(
   data: DownloadRequest, 
   db = Depends(get_db),
   user_id = Depends(verify_web_user),
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
    

@web_passwords.delete("/backups/{backup_id}")
async def web_delete_backup(
   backup_id: int, 
   db = Depends(get_db),
   user_id = Depends(verify_web_user),
):
    dao = BackupDao(session=db)
    deleted_backup = await dao.delete_backup_by_id(backup_id=backup_id, user_id=user_id)
    if deleted_backup is None:
        raise HTTPException(404, detail=f"Backup with '{backup_id}' id was not found at your account")
    
    #delete file local
    delete_backup_by_path(backup_path=Path(deleted_backup.path))
    
    return MessageResponse(
        ok=True,
        detail="Your backup was successully deleted"
    )


