from pathlib import Path
import shutil

from src.core.settings import BACKUPS


def get_user_backup_path(user_id: int, backup_id: int) -> Path:
    backup_dir = BACKUPS / str(user_id) / str(backup_id)
    backups = [b for b in backup_dir.glob("*.json")] #1 file
    return backups[0]

def delete_backup_by_path(backup_path: Path) -> None:
    backup_folder = backup_path.parent
    shutil.rmtree(backup_folder)