import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from backend.password_manager.core.password_tool import PasswordTool
from backend.password_manager.core.crypto import derive_key, create_dek, create_random_salt
from backend.dao.userDao import UserDao, Users
from backend.dao.vaultDao import VaultDao, VaultFields
from backend.schemas.db_schema import CreateUserInDb

VAULT_NAME = "Vault"


@pytest_asyncio.fixture
async def db_user(db_session: AsyncSession):
    dao = UserDao(session=db_session)
    data = CreateUserInDb(username="test", password_hash="password_hash")
    user = await dao.create_user(user_data=data, role_id=1) # doesnot matter data and role id
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def password_tool(db_user: Users, db_session: AsyncSession):
    salt = create_random_salt()
    master_password = "Master Password"
    kek = derive_key(master_password=master_password, salt_b64=salt)
    dek, encrypted_dek = create_dek(kek=kek)

    dao = VaultDao(session=db_session)
    vault = await dao.create_vault(
        user_id=db_user.id,
        name=VAULT_NAME,
        encrypted_passwords="",
        salt=salt,
        encrypted_dek=encrypted_dek
    )
    
    pas_tool = PasswordTool(
        user_id=db_user.id,
        vault=vault,
        dek=dek,
        session=db_session
    )
    await db_session.commit()
    
    return pas_tool

@pytest_asyncio.fixture
async def db_vault(db_user: Users, db_session: AsyncSession):
    dao = VaultDao(session=db_session)
    vault = await dao.get_vault_by_field(field=VaultFields.NAME, value=VAULT_NAME, user_id=db_user.id)
    assert vault is not None
    return vault