import pytest

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from backend.dao.backupDao import BackupDao



@pytest.mark.asyncio
async def test_pin_change__double_pin__toggles_state(client: AsyncClient, jwt_bearer_mock, test_user, db_session: AsyncSession, test_backup):
    user_id = test_user.id
    dao = BackupDao(session=db_session)
    backup_id = test_backup.id
    
    #first change pin
    url = f"/api/backups/{backup_id}/change-pin"
    response = await client.patch(
        url=url,
    )
    assert response.status_code == 200
    backup = await dao.get_backup_by_id(backup_id=backup_id, user_id=user_id)
    await db_session.refresh(backup)
    assert backup is not None
    assert backup.pinned == True
    
    #second change pin
    response = await client.patch(
        url=url,
    )
    assert response.status_code == 200
    backup = await dao.get_backup_by_id(backup_id=backup_id, user_id=user_id)
    await db_session.refresh(backup)
    assert backup is not None
    assert backup.pinned == False
    
@pytest.mark.asyncio
async def test_pin_change__wrong_backup__returns_not_found(client: AsyncClient, jwt_bearer_mock):
    url = "/api/backups/404/change-pin"
    response = await client.patch(
        url=url,
    )
    assert response.status_code == 404