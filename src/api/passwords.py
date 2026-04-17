from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import shutil


from src.dependincies import get_db
from src.dao.backupDao import BackupDao







passwords = APIRouter()


@passwords.post("/backups/upload")
async def upload_post(
    user_id: int, #jwt.validate_user
    file: UploadFile = File(...),
    db = Depends(get_db),
):
    dao = BackupDao(db)
    if file.filename is None:
        raise HTTPException(401, detail="Filename is None")
    
    new_backup = dao.create_backup(user_id, file.filename)
    async with new_backup as backup:
        content = await file.read()
        with open(backup.path, "wb") as f:
            f.write(content)

        return {
            "ok": True,
            "message": f"Your backup was successfully uploaded"
        }
    
    








