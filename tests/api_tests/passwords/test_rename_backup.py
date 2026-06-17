import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.db_schema import UserFields
from src.schemas.base import LoginRequest, RegisterRequestData
from src.dao.backupDao import BackupDao
from src.dao.userDao import UserDao
import src.dao.backupDao as dao_file


@pytest.mark.asyncio
async def test_rename(client: AsyncClient, jwt_bearer_mock, test_user, db_session: AsyncSession, test_backup):
    user_id = test_user.id
    dao = BackupDao(session=db_session)
    backups = await dao.get_user_backups(user_id=user_id)
    assert backups
    backup = backups[0]
    
    url = f"/api/backups/{backup.id}"
    new_name = "new_name"
    response = await client.patch(
        url=url,
        json=new_name
    )
    
    assert response.status_code == 200
    
    backup = await dao.get_backup_by_id(backup_id=backup.id, user_id=user_id)
    await db_session.refresh(backup)
    
    assert backup
    assert backup.name == new_name
    

@pytest.mark.asyncio
async def test_rename_with_empty_name(client: AsyncClient, jwt_bearer_mock, test_user, db_session: AsyncSession, test_backup):
    user_id = test_user.id
    dao = BackupDao(session=db_session)
    backups = await dao.get_user_backups(user_id=user_id)
    assert backups
    backup = backups[0]
    
    url = f"/api/backups/{backup.id}"
    new_name = ""
    response = await client.patch(
        url=url,
        json=new_name
    )
    
    assert response.status_code == 422
    
@pytest.mark.asyncio
async def test_rename_someones_backup(client: AsyncClient, db_session: AsyncSession, tmp_path, monkeypatch):
    #create first user
    first_username = "test_user_1"
    password = "password"
    data = RegisterRequestData(
        username=first_username, password=password, telegram_id=1910592094
    )
    response = await client.post(url="/api/register", json=data.model_dump())
    assert response.status_code == 201
    
    #login first user
    login_data = LoginRequest(
        username=first_username,
        password=password
    )
    response = await client.post(url="/api/login", json=login_data.model_dump())
    assert response.status_code == 200
    data = response.json()
    bearer_token = data.get("bearer_token").get("token")
    assert bearer_token is not None
    
    #create backup
    file_path = tmp_path / "test_backup.json"
    backup_data = b"My backup data"
    file_path.write_bytes(backup_data)
    monkeypatch.setattr(dao_file, "BACKUPS", tmp_path)
    with open(file_path, "rb") as f:
        response = await client.post(
            url="/api/backups/upload",
            files={"file": (file_path.name, f)},
            data={"name": "backup_name", "rows": 4},
            headers={"Authorization": f"Bearer {bearer_token}"}
        )
        
    assert response.status_code == 201
    
    #get first user from db
    user_dao = UserDao(session=db_session)
    user = await user_dao.get_user_by_field(field=UserFields.USERNAME, value=first_username)
    assert user is not None
    
    #get created backup
    user_id = user.id
    dao = BackupDao(session=db_session)
    backups = await dao.get_user_backups(user_id=user_id)
    assert backups
    backup = backups[0]
    
    #register second user
    second_username = "test_user_2"
    data = RegisterRequestData(
        username=second_username, password=password, telegram_id=1910592093
    )
    response = await client.post(url="/api/register", json=data.model_dump())
    assert response.status_code == 201
    
    #login second user
    login_data = LoginRequest(
        username=second_username,
        password=password
    )
    response = await client.post(url="/api/login", json=login_data.model_dump())
    assert response.status_code == 200
    data = response.json()
    bearer_token = data.get("bearer_token").get("token")
    assert bearer_token is not None
    
    #rename backup
    url = f"/api/backups/{backup.id}"
    response = await client.patch(
        url=url,
        json="new_name",
        headers={"Authorization": f"Bearer {bearer_token}"} #Token of second user
    )
    
    assert response.status_code == 404

    