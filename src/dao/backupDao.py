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
        self, user_id: int, filename: str
    ) -> AsyncGenerator[Backups, None]:
        new_backup = Backups(
            user_id=user_id,
            # path=path,
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
        query = select(Backups).where(Backups.user_id == user_id)
        result = await self.session.execute(query)
        backups = result.scalars().all()
        return backups
