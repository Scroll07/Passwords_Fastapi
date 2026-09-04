import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from backend.password_manager.core.password_tool import PasswordTool
from backend.password_manager.core.crypto import derive_key, create_dek, create_random_salt
from backend.dao.userDao import UserDao, Users
from backend.dao.vaultDao import VaultDao, Vaults
from backend.schemas.db_schema import CreateUserInDb

@pytest_asyncio.fixture
async def db_user(db_session: AsyncSession):
    dao = UserDao(session=db_session)
    data = CreateUserInDb(username="test", password_hash="password_hash")
    user = await dao.create_user(user_data=data, role_id=1) # doesnot matter data and role id
    return user


@pytest_asyncio.fixture
async def db_vault(db_user: Users, db_session: AsyncSession):
    dao = VaultDao(session=db_session)
    vault = await dao.create_vault(
        user_id=db_user.id,
        name="vault",
        encrypted_passwords="",
        salt="does not matter",
        encrypted_dek=b'does not matter'
    )
    return vault


@pytest.fixture
def password_tool(db_user: Users, db_vault: Vaults, db_session: AsyncSession):
    salt = create_random_salt()
    master_password = "Master Password"
    kek = derive_key(master_password=master_password, salt_b64=salt)
    # or kek = cryptography.fernet.generate_key (there is no difference)
    dek, encrypted_dek = create_dek(kek=kek)
    
    pas_tool = PasswordTool(
        user_id=db_user.id,
        vault=db_vault,
        dek=dek,
        session=db_session
    )
    return pas_tool