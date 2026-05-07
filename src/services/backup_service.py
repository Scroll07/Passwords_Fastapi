from src.core.settings import BACKUPS
from pathlib import Path

def get_user_backup_path(user_id: int, backup_id: int) -> Path:
    backup_dir = BACKUPS / str(user_id) / str(backup_id)
    backups = [b for b in backup_dir.glob("*.json")] #1 file
    return backups[0]