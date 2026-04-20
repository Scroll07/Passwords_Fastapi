from sqlalchemy.ext.asyncio import AsyncSession
from src.models.model import Users
from sqlalchemy import select

from src.schemas.base import RegisterRequestData, GetUserFields


class UserDao:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, user_data: RegisterRequestData):
        new_user = Users(
            username=user_data.username,
            password_hash=user_data.password,
            telegram_id=user_data.telegram_id,
        )
        self.session.add(new_user)
        await self.session.flush()
        await self.session.refresh(new_user)
        await self.session.commit()

        return new_user

    async def get_user_hash(self, username: str) -> str | None:
        query = select(Users.password_hash).where(Users.username == username)
        result = await self.session.execute(query)
        hash = result.scalar_one_or_none()
        return hash

    async def get_user_by_field(
        self, field: GetUserFields, value: str | int
    ) -> Users | None:
        column = getattr(Users, field)
        qeury = select(Users).where(column == value)
        result = await self.session.execute(qeury)
        user = result.scalar_one_or_none()
        return user
