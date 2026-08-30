from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.schemas.dao_schemas import UserWithRole, UserData
from backend.schemas.db_schema import UserFields, UserInDb, UserRoles
from backend.models.model import Users, Roles
from backend.schemas.db_schema import CreateUserInDb
from backend.dependencies import get_settings
from backend.dao.role_dao import RoleDAO
from backend.services.secrets import hash_password

class UserDao:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, user_data: CreateUserInDb, role_id: int):
        new_user = Users(
            username=user_data.username,
            password_hash=user_data.password_hash,
            telegram_id=user_data.telegram_id,
            role_id=role_id
        )
        self.session.add(new_user)
        await self.session.flush()
        # await self.session.refresh(new_user)
        # await self.session.commit()

        return new_user

    async def get_user_hash(self, username: str) -> str | None:
        query = select(Users.password_hash).where(Users.username == username)
        result = await self.session.execute(query)
        hash = result.scalar_one_or_none()
        return hash

    async def get_user_by_field(
        self, field: UserFields, value: str | int
    ) -> Users | None:
        column = getattr(Users, field)
        qeury = select(Users).where(column == value)
        result = await self.session.execute(qeury)
        user = result.scalar_one_or_none()
        return user

    async def change_password(self, user: Users, new_hash: str) -> Users | None:
        if not user:
            return None
        user.password_hash = new_hash
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_user_with_role(self, user_id: int) -> UserWithRole | None:
        query = select(Users, Roles.name).join(Roles, Users.role_id == Roles.id).where(Users.id == user_id)
        result = await self.session.execute(query)
        data = result.one_or_none()
        if data is None:
            return None
        return UserWithRole(
            user=UserInDb.model_validate(data[0]),
            role=data[1]
        ) 
    
    async def initialize_admins(self) -> None:
        s = get_settings()
        if s.ADMIN_USERNAME is None or s.ADMIN_PASSWORD is None:
            raise ValueError("Admin login or password must not be None")
        admin = await self.get_user_by_field(field=UserFields.USERNAME, value=s.ADMIN_USERNAME)
        if admin is not None:
            return None
        
        role_dao = RoleDAO(session=self.session)
        admin_role = await role_dao.get_role(UserRoles.ADMIN)
        if not admin_role:
            raise ValueError("No admin role, initialization failed")
        hash = hash_password(password=s.ADMIN_PASSWORD)
        data = CreateUserInDb(
            username=s.ADMIN_USERNAME,
            password_hash=hash,
        )
        await self.create_user(user_data=data, role_id=admin_role.id)
        
        return None
    
    async def get_user_data(self, user_id: int) -> UserData | None:
        user = await self.get_user_by_field(field=UserFields.ID, value=user_id)
        if not user:
            return None
        query = select(Roles.name).where(Roles.id == user.role_id)
        result = await self.session.execute(query)
        role_name = result.scalar_one()
        
        user_data = UserData(
            id=user.id,
            username=user.username,
            telegram_id=user.telegram_id,
            is_active=user.is_active,
            created_at=user.created_at,
            role=role_name
        ) 
        return user_data