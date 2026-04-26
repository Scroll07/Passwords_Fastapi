from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from src.dependincies import get_db, verify_user
from src.dao.backupDao import BackupDao
from src.core.logger import get_logger


logger = get_logger(__name__)

passwords = APIRouter()


@passwords.post("/backups/upload")
async def upload_post(
    file: UploadFile = File(...),
    db=Depends(get_db),
    user_id=Depends(verify_user),
):
    try:
        dao = BackupDao(db)
        if file.filename is None:
            raise HTTPException(401, detail="Filename is None")

        new_backup = dao.create_backup(user_id, file.filename)
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


# @passwords.post("/backups/download")
# async def download_post(
#    db = Depends(get_db),
#    user_id = Depends(verify_user)
# ):
#    pass