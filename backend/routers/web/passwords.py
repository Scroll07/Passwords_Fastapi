from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Body, Form, Request, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from pydantic import ValidationError

from backend.schemas.jinja_context import UserBackupContext
from backend.core.templates import templates
from backend.schemas.jwt import JWTDecodedData
from backend.schemas.api_responses import BackupsResponse, MessageResponse
from backend.schemas.base import BackupData, DownloadRequest
from backend.dependincies import get_db, verify_user
from backend.dao.backupDao import BackupDao
from backend.core.logger import get_logger
from backend.services.backup_service import delete_backup_by_path
from backend.schemas.base import SortByBackups

logger = get_logger(__name__)

web_passwords = APIRouter()


#==============================
#            WEB    
#==============================
from backend.dependincies import verify_web_user


@web_passwords.get("/backups")
async def web_get_user_backups(
    db = Depends(get_db),
    token_data: JWTDecodedData = Depends(verify_web_user),
    sort_by: SortByBackups = Query(SortByBackups.CREATED_AT)
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
        if sort_by == SortByBackups.CREATED_AT:
            backups_data = sorted(backups_data, key=lambda x: x.created_at, reverse=True)
        elif sort_by == SortByBackups.ROWS:
            backups_data = sorted(backups_data, key=lambda x: x.rows, reverse=True)
        elif sort_by == SortByBackups.NAME:
            backups_data = sorted(backups_data, key=lambda x: x.name, reverse=False)
        
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


@web_passwords.post("/backups/{backup_id}/change-pin", response_class=HTMLResponse)
async def web_change_pin(
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
        user_backup.pinned = not user_backup.pinned
        await db.commit()
        
        action = "pinned" if user_backup.pinned else "unpinned"
        response = templates.TemplateResponse(
            request=request,
            name="user_backup.html",
            context=UserBackupContext(
                backup=backup,
                success=f"Your backup was successully {action}"
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