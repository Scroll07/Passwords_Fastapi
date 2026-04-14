from sqlalchemy.ext.asyncio import AsyncSession
from src.models.model import Users


from schemas.base import RegisterRequestData

class UserDao:
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession

    async def create_user(self, user_data: RegisterRequestData):
        new_user = Users(
            username=user_data.username,
            password_hash=user_data.password,
            telegram_id=user_data.telegram_id
        )
        self.session.add(new_user)
        await self.session.flush()
        await self.session.commit()
        
        return new_user
    
    

