from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Body, Form, Request, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from pydantic import ValidationError

from src.schemas.jinja_context import UserBackupContext
from src.core.templates import templates
from src.schemas.jwt import JWTDecodedData
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

# @web_passwords.post("/backups/upload")
# async def web_upload_post(
#     name: str = Form(...),
#     rows: int = Form(...),
#     file: UploadFile = File(...),
#     db=Depends(get_db),
#     user_id=Depends(verify_web_user),
# ):
#     try:
#         if user_id is None:
#             return RedirectResponse(url="/web/login")
#         dao = BackupDao(db)
#         if file.filename is None:
#             raise HTTPException(401, detail="Filename is None")

#         new_backup = dao.create_backup(user_id=user_id, filename=file.filename, name=name, rows=rows)
#         async with new_backup as backup:
#             content = await file.read()
#             with open(backup.path, "wb") as f:
#                 f.write(content)

#             response = MessageResponse(
#                 ok=True,
#                 detail="Your backup was successfully uploaded"
#             )
#             return response

#     except HTTPException as e:
#         logger.warning(e)
#         raise e
#     except Exception as e:
#         logger.exception(e)
#         raise HTTPException(500, "Internal server error")


@web_passwords.get("/`backups`")
async def web_get_user_backups(
    db = Depends(get_db),
    token_data: JWTDecodedData = Depends(verify_web_user),
):
    try:
        dao = BackupDao(session=db)
        backups = await dao.get_user_backups(user_id=int(token_data.sub))
        backups_data = [
            BackupData(
                id=b.id,
                name=b.name,
                rows=b.rows,
                pinned=b.pinned,
                created_at=b.created_at,
            )
            for b in backups
        ]
        response = BackupsResponse(
            ok=True,
            detail=f"Backups of {int(token_data.sub)}",
            backups=backups_data
        )
        
        return response
    except Exception as e:
        logger.exception(f"Error in Backups handler: {e}")
        raise HTTPException(500, detail="Interal server error")
    

@web_passwords.post("/backups/{backup_id}/download")
async def web_download_post(
   backup_id: int, 
   db = Depends(get_db),
   token_data: JWTDecodedData = Depends(verify_web_user),
):
    try:
        dao = BackupDao(session=db)
        backup = await dao.get_backup_by_id(backup_id=backup_id, user_id=int(token_data.sub))
        if backup is None:
            raise HTTPException(404, "Backup was not found")
            
        if not Path(backup.path).exists():
            raise HTTPException(500, "We cant find your backup")
        
        now = datetime.now()
        date = datetime.strftime(now, format="%Y-%m-%d_%H-%M-%S")
        
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
    

@web_passwords.post("/backups/{backup_id}/rename", response_class=HTMLResponse)
async def web_patch_backup(
   request: Request,
   backup_id: int, 
   new_name: str = Form(...),
   db = Depends(get_db),
   token_data: JWTDecodedData = Depends(verify_web_user),
):
    try:
        dao = BackupDao(session=db)
        user_backup = await dao.get_backup_by_id(backup_id=backup_id, user_id=int(token_data.sub))
        if not user_backup:
            error = "This Backup was not found at your account"
            return RedirectResponse(
                url=f"/web/404?error={error}",
                status_code=303
            )
        backup = BackupData.model_validate(user_backup)
    
    except Exception as e:
        raise HTTPException(500, "Internal server error")          
    
    new_name = new_name.strip()
    if not new_name:
        return templates.TemplateResponse(
            request=request,
            name="user_backup.html",
            context=UserBackupContext(
                backup=backup,
                error="New name can not be empty"
            ).model_dump()
        )
        
    if len(new_name) > 20:
        return templates.TemplateResponse(
            request=request,
            name="user_backup.html",
            context=UserBackupContext(
                backup=backup,
                error="String should have at most 20"
            ).model_dump()
        )
    
    try:
        user_backup.name = new_name
        await db.commit()
        backup.name = new_name
        
                
        response = templates.TemplateResponse(
            request=request,
            name="user_backup.html",
            context=UserBackupContext(
                backup=backup,
                success="Your backup was successully renamed"
            ).model_dump()
        )
        
        return response
    
    except HTTPException as e:
        logger.warning(e)
        return templates.TemplateResponse(
            request=request,
            name="user_backup.html",
            context=UserBackupContext(
                backup=backup,
                error=e.detail,
            ).model_dump()
        )

    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error") 

@web_passwords.post("/backups/{backup_id}/delete", response_class=RedirectResponse)
async def web_delete_backup(
   request: Request,
   backup_id: int, 
   db = Depends(get_db),
   token_data: JWTDecodedData = Depends(verify_web_user),
):
    try:
        dao = BackupDao(session=db)
        user_backup = await dao.get_backup_by_id(backup_id=backup_id, user_id=int(token_data.sub))
        if not user_backup:
            error = "This Backup was not found at your account"
            return RedirectResponse(
                url=f"/web/404?error={error}",
                status_code=303
            )
        backup = BackupData.model_validate(user_backup)
    
    except Exception as e:
        raise HTTPException(500, "Internal server error")  
    
    try:
        dao = BackupDao(session=db)
        deleted_backup = await dao.delete_backup_by_id(backup_id=backup_id, user_id=int(token_data.sub))
        if deleted_backup is None:
            raise ValueError("No deleted backup")
        
        #delete file local
        delete_backup_by_path(backup_path=Path(deleted_backup.path))
        
        
        return RedirectResponse(
            url="/web/dashboard",
            status_code=303
        )

    except HTTPException as e:
        logger.warning(e)
        return templates.TemplateResponse(
            request=request,
            name="user_backup.html",
            context=UserBackupContext(
                backup=backup,
                error=e.detail,
            ).model_dump()
        )

    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error") 
