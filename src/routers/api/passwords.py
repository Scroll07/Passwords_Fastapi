from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Body, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse

from src.schemas.jwt import JWTDecodedData
from src.schemas.api_responses import BackupsResponse, MessageResponse
from src.schemas.base import BackupData, DownloadRequest
from src.dependincies import get_db, verify_user
from src.dao.backupDao import BackupDao
from src.core.logger import get_logger
from src.services.backup_service import delete_backup_by_path

logger = get_logger(__name__)

api_passwords = APIRouter()

#==============================
#            API    
#==============================
@api_passwords.post("/backups/upload", status_code=201)
async def upload_post(
    name: str = Form(...),
    rows: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    data: JWTDecodedData= Depends(verify_user),
):
    try:
        dao = BackupDao(db)
        if file.filename is None:
            raise HTTPException(401, detail="Filename is None")

        new_backup = dao.create_backup(user_id=int(data.sub), filename=file.filename, name=name, rows=rows)
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


@api_passwords.get("/backups")
async def get_user_backups(
    db: AsyncSession = Depends(get_db),
    data: JWTDecodedData = Depends(verify_user),
):
    try:
        dao = BackupDao(session=db)
        user_id_int = int(data.sub)
        backups = await dao.get_user_backups(user_id=user_id_int)
        backups_data = [
            BackupData(
                id=b.id,
                created_at=b.created_at,
                name=b.name,
                rows=b.rows,
                pinned=b.pinned
            )
            for b in backups
        ]
        response = BackupsResponse(
            ok=True,
            detail=f"Backups of {user_id_int}",
            backups=backups_data
        )
        
        return response
    except Exception as e:
        logger.exception(f"Error in Backups handler: {e}")
        raise HTTPException(500, detail="Interal server error")
    

@api_passwords.post("/backups/download")
async def download_post(
   req: DownloadRequest, 
   db: AsyncSession = Depends(get_db),
   data: JWTDecodedData = Depends(verify_user),
):
    try:
        dao = BackupDao(session=db)
        backup = await dao.get_backup_by_id(backup_id=req.backup_id, user_id=int(data.sub))
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
    

@api_passwords.delete("/backups/{backup_id}")
async def delete_backup(
   backup_id: int, 
   db: AsyncSession = Depends(get_db),
   data: JWTDecodedData = Depends(verify_user),
):
    dao = BackupDao(session=db)
    deleted_backup = await dao.delete_backup_by_id(backup_id=backup_id, user_id=int(data.sub))
    if deleted_backup is None:
        raise HTTPException(404, detail=f"Backup with '{backup_id}' id was not found at your account")
    
    #delete file local
    delete_backup_by_path(backup_path=Path(deleted_backup.path))
    
    return MessageResponse(
        ok=True,
        detail="Your backup was successully deleted"
    )

@api_passwords.patch("/backups/{backup_id}")
async def patch_backup(
   backup_id: int, 
   new_name: str = Body(..., min_length=1, max_length=20),
   db: AsyncSession = Depends(get_db),
   data: JWTDecodedData = Depends(verify_user),
):
    dao = BackupDao(session=db)
    pathced_backup = await dao.rename_backup_by_id(backup_id=backup_id, user_id=int(data.sub), new_name=new_name)
    if pathced_backup is None:
        raise HTTPException(404, detail=f"Backup with '{backup_id}' id was not found at your account")
         
    return MessageResponse(
        ok=True,
        detail="Your backup was successully renamed"
    )

@api_passwords.patch("/backups/{backup_id}/change-pin")
async def pin_backup(
   backup_id: int, 
   db: AsyncSession = Depends(get_db),
   data: JWTDecodedData = Depends(verify_user),
):
    try:
        dao = BackupDao(session=db)
        backup = await dao.change_pin_backup(backup_id=backup_id, user_id=int(data.sub))
        if not backup:
            raise HTTPException(404, "No backup with such data")
        action = "pinned" if backup.pinned else "unpinned" 
        
        await db.commit()
        return MessageResponse(
            ok=True,
            detail=f"Your backup was successully {action}"
        )
    except HTTPException as e:
        logger.exception(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")





