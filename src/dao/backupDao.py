from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from contextlib import asynccontextmanager
from typing import Sequence, AsyncGenerator

from src.schemas.db_schema import BackupStats
from src.core.settings import BACKUPS
from src.models.model import Backups

class BackupDao:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @asynccontextmanager
    async def create_backup(
        self, user_id: int, filename: str, rows: int, name: str, pinned: bool = False
    ) -> AsyncGenerator[Backups, None]:
        new_backup = Backups(
            user_id=user_id,
            rows=rows,
            name=name,
            pinned=pinned
        )
        self.session.add(new_backup)

        await self.session.flush()
        await self.session.refresh(new_backup)

        backup_dir = BACKUPS / str(user_id) / str(new_backup.id)
        backup_dir.mkdir(exist_ok=True, parents=True)
        path = backup_dir / filename

        new_backup.path = str(path)

        try:
            yield new_backup

            await self.session.commit()

        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_user_backups(self, user_id: int) -> Sequence[Backups]:
        query = select(Backups).where(Backups.user_id == user_id).limit(10)
        result = await self.session.execute(query)
        backups = result.scalars().all()
        return backups

    async def get_backup_by_id(self, backup_id: int, user_id: int) -> Backups | None:
        query = select(Backups).where(Backups.id == backup_id, Backups.user_id == user_id)
        result = await self.session.execute(query)
        backup = result.scalar_one_or_none()
        return backup
    
    async def delete_backup_by_id(self, backup_id: int, user_id: int) -> Backups | None:
        backup_to_delete = await self.get_backup_by_id(backup_id=backup_id, user_id=user_id)
        if backup_to_delete is None:
            return None
        await self.session.delete(backup_to_delete)
        await self.session.commit()
        return backup_to_delete
    
    async def rename_backup_by_id(self, backup_id: int, user_id: int, new_name: str) -> Backups | None:
        backup = await self.get_backup_by_id(backup_id=backup_id, user_id=user_id)
        if not backup:
            return None
        backup.name = new_name
        await self.session.commit()
        await self.session.refresh(backup)
        return backup
    
    async def change_pin_backup(self, backup_id: int, user_id: int) -> Backups | None:
        backup = await self.get_backup_by_id(backup_id=backup_id, user_id=user_id)
        if not backup:
            return None
        backup.pinned = not backup.pinned
        return backup
        
        
    
    
    # async def stats__get_count_backups(self, user_id: int) -> int:
    #     query = select(func.count(Backups.id)).where(Backups.user_id == user_id)
    #     result = await self.session.execute(query)
    #     count = result.scalar_one()
    #     return count
    
    # async def stats__get_max_rows(self, user_id: int) -> int:
    #     query = select(func.max(Backups.rows)).where(Backups.user_id == user_id)
    #     result = await self.session.execute(query)
    #     max_rows = result.scalar_one()
    #     return max_rows
    
    # async def stats__get_min_rows(self, user_id: int) -> int:
    #     query = select(func.min(Backups.rows)).where(Backups.user_id == user_id)
    #     result = await self.session.execute(query)
    #     max_rows = result.scalar_one()
    #     return max_rows 
    
    # async def stats__get_avg_rows(self, user_id: int) -> int:
    #     query = select(func.avg(Backups.rows)).where(Backups.user_id == user_id)
    #     result = await self.session.execute(query)
    #     max_rows = result.scalar_one()
    #     return max_rows 
        
    # async def stats__get_count_backups_for_week(self, user_id: int) -> int:
    #     query = select(func.count(Backups.id)).where(
    #         Backups.user_id == user_id,
    #         Backups.created_at > datetime.now(timezone.utc) - timedelta(days=7)
    #     )
    #     result = await self.session.execute(query)
    #     count = result.scalar_one()
    #     return count
    
    async def stats__get_user_stats(self, user_id: int) -> BackupStats:
        query = select(
            func.count(Backups.id),
            func.max(Backups.rows),
            func.min(Backups.rows),
            func.avg(Backups.rows),
            func.count(Backups.id).filter(Backups.created_at > datetime.now(timezone.utc) - timedelta(days=7))
        ).where(Backups.user_id == user_id)
        result = await self.session.execute(query)
        row = result.one()
        return BackupStats(
            backups_count=row[0] or 0,
            max_rows=row[1] or 0,
            min_rows=row[2] or 0,
            avg_rows=row[3] or 0,
            backups_for_week=row[4] or 0
        )