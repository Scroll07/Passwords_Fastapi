from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from contextlib import asynccontextmanager
from typing import Sequence, AsyncGenerator

from backend.schemas.db_schema import BackupStats
from backend.models.model import Vaults


# Auto Commit at the end of every method
class VaultDao:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        
    async def create_vault(
        self,
        user_id: int,
        name: str,
        encrypted_passwords: str,
        salt: str,
        encrypted_dek: bytes
    ) -> Vaults:
        new_vault = Vaults(
            user_id=user_id,
            name=name,
            encrypted_passwords=encrypted_passwords,
            salt=salt,
            encrypted_dek=encrypted_dek      
        )
        
        self.session.add(new_vault)
        await self.session.flush()
        await self.session.commit()
        return new_vault
    
    async def get_vault(self, user_id: int, vault_id: int) -> Vaults | None:
        query = select(Vaults).where(Vaults.user_id == user_id, Vaults.id == vault_id)
        result = await self.session.execute(query)
        vault = result.scalar_one_or_none()
        return vault
    
    async def delete_vault(self, user_id: int, vault_id: int) -> Vaults | None:
        vault_to_delete = await self.get_vault(user_id=user_id, vault_id=vault_id)
        if not vault_to_delete:
            return None
        await self.session.delete(vault_to_delete)
        await self.session.commit()
        return vault_to_delete
            
        