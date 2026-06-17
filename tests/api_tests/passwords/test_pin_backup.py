import pytest

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.backupDao import BackupDao



@pytest.mark.asyncio
async def test_duouble_pin_backup(client: AsyncClient, jwt_bearer_mock, test_user, db_session: AsyncSession, test_backup):
    user_id = test_user.id
    dao = BackupDao(session=db_session)
    backups = await dao.get_user_backups(user_id=user_id)
    assert backups
    backup = backups[0]
    backup_id = backup.id
    print(f"BACKUP PINNED BEFORE AFTER CREATED BACKUP: {backup.pinned}")
    
    #first change pin
    url = f"/api/backups/{backup_id}/change-pin"
    response = await client.patch(
        url=url,
    )
    print(f'RESPONSE DATA: {response.json()}')
    assert response.status_code == 200
    backup = await dao.get_backup_by_id(backup_id=backup_id, user_id=user_id)
    await db_session.refresh(backup)
    assert backup is not None
    assert backup.pinned == True
    
    #second change pin
    response = await client.patch(
        url=url,
    )
    print(f'RESPONSE DATA: {response.json()}')
    assert response.status_code == 200
    backup = await dao.get_backup_by_id(backup_id=backup_id, user_id=user_id)
    await db_session.refresh(backup)
    assert backup is not None
    assert backup.pinned == False
    
@pytest.mark.asyncio
async def test_pin_wrong_backup(client: AsyncClient, jwt_bearer_mock):
    url = "/api/backups/404/change-pin"
    response = await client.patch(
        url=url,
    )
    assert response.status_code == 404