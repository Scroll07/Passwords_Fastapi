from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
from typing import Sequence, AsyncGenerator
from src.models.model import Backups
from src.core.settings import BACKUPS


class BackupDao:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @asynccontextmanager
    async def create_backup(
        self, user_id: int, filename: str, rows: int, name: str
    ) -> AsyncGenerator[Backups, None]:
        new_backup = Backups(
            user_id=user_id,
            rows=rows,
            name_to_show=name
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
        backup.name_to_show = new_name
        await self.session.commit()
        await self.session.refresh(backup)
        return backup
        
        