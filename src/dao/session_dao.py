from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence

from src.models.model import Sessions


class SessionDao:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        
    async def create_session(self, user_id: int, expires_at: datetime,) -> Sessions:
        new_session = Sessions(
            user_id=user_id,
            expires_at=expires_at
        )
        self.session.add(new_session)
        await self.session.flush()
        # await self.session.commit()
        return new_session
    
    async def get_session(self, session_id: int) -> Sessions | None:
        query = select(Sessions).where(Sessions.id == session_id)
        result = await self.session.execute(query)
        session = result.scalar_one_or_none()
        return session
    
    async def get_active_user_sessions(self, user_id: int) -> Sequence[Sessions]:
        query = select(Sessions).where(Sessions.user_id == user_id, Sessions.is_active == True)
        result = await self.session.execute(query)
        sessions = result.scalars().all()
        return sessions
    
    async def make_unactive_session(self, user_id: int) -> None:
        sessions = await self.get_active_user_sessions(user_id=user_id)
        if not sessions:
            raise ValueError("No session to delete")
        for session in sessions:
            session.is_active = False
        # await self.session.commit()



