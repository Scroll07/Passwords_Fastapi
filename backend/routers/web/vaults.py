from fastapi import APIRouter, Body, Form, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import InvalidToken


from backend.services.jwt_service import JWT_Service
from backend.dao.userDao import UserDao
from backend.schemas.jwt import JWTDecodedData
from backend.schemas.base import CreateVaultData, SortByVaults, VaultData
from backend.schemas.db_schema import SessionType
from backend.dependencies import get_db, get_jwt_service
from backend.web_dependencies import verify_web_user, web__check_vault_exists
from backend.core.logger import get_logger
from backend.schemas.requests import RequstVaultDependecie
from backend.dao.vaultDao import VaultDao, VaultFields
from backend.services.secrets import (
    hash_password,
    verify_password
)
from backend.services.jwt_service import create_token_and_session
from backend.password_manager.services.password import (
    create_user_vault,
    check_is_vault_exists
)
from backend.password_manager.core.crypto import (
    derive_key,
    decrypt_dek,
    decrypt_vault_passwords,
    encrypt_vault_passwords
)
from backend.services.cookies import add_vault_cookie


logger = get_logger(__name__)

web_vaults = APIRouter()


#Ручка чтобы создать персональный файл с шифрованием

# + добавить функцию чтобы проверять создан ли файл у пользвоателя 
# (функция должна быть где-то в services или в dependencies)

# Добавь логи к каждой ручке

# Добавить роутер для скачивания vault file (Но сначала переделай cli)

@web_vaults.post('/create-vault')
async def create_vault__router(
    vault_name: str = Body(...),
    vault_master_password: str = Body(...),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        # Получить информацию пользователя (username  и т.д.)
        user_id = int(token_data.sub)
        dao = UserDao(session=db)
        user_data = await dao.get_user_data(user_id=user_id)
        if not user_data:
            raise HTTPException(404, "Wrong user data")
        
        # Проверить существует ли `vault`
        vault_name = vault_name.strip()
        vault_dao = VaultDao(session=db)
        vault = await vault_dao.get_vault_by_field(field=VaultFields.NAME, value=vault_name, user_id=user_id)
        if vault:
            raise HTTPException(409, "Vault with such name alredy exists")
        
        # Провалидировать данные
        vault_data = CreateVaultData(
            name=vault_name,
            master_password=vault_master_password
        )
        
        # Создать Vault
        encrypted_data = create_user_vault(master_password=vault_master_password)  # encrypted_passwords: str encrypted_dek: bytes
        
        # Сохранить данные в бд
        vault_dao = VaultDao(session=db)
        await vault_dao.create_vault(
            user_id=user_id,
            name=vault_name,
            encrypted_passwords=encrypted_data.encrypted_passwords,
            salt=encrypted_data.salt,
            encrypted_dek=encrypted_data.encrypted_dek
        )
        
        return {
            "ok": True,
            "detail": "New vault was successfully created"
        }
        
    except HTTPException as e:
        raise e
    except ValidationError as e:
        raise HTTPException(401, e.errors)
    except Exception as e:
        raise HTTPException(500, 'Internal server error')
    

@web_vaults.delete('/vaults/{vault_id}')
async def delete_vault__router(
    vault_id: int,
    vault_data: RequstVaultDependecie = Depends(web__check_vault_exists),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_data.sub)
    vault_dao = VaultDao(session=db)
    deleted_vault = await vault_dao.delete_vault(user_id=user_id, vault_id=vault_id)
    if not deleted_vault:
        raise HTTPException(401, "Wrong vault data")
    
    return {
        "ok": True,
        "detail": "Vault was successfully deleted"
    }
    
    
@web_vaults.post('/vaults/{vault_id}/rename')
async def rename_vault__router(
    vault_id: int,
    new_name: str = Body(min_length=1),
    vault_data: RequstVaultDependecie = Depends(web__check_vault_exists),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
):
    vault_data.vault.name = new_name.strip()
    await db.commit()
    
    return {
        "ok": True,
        "detail": "Vault was successfully renamed"
    }
    
    
@web_vaults.get('/vaults')
async def get_user_vaults__router(
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
    sort_by: SortByVaults = Query(SortByVaults.CREATED_AT)
):
    user_id = int(token_data.sub)
    dao = VaultDao(session=db)
    vaults = await dao.get_user_vaults(user_id=user_id)
    
    vaults_data = [
        VaultData(
            id=v.id,
            name=v.name,
            entries=v.entries,
            pinned=v.pinned,
            created_at=v.created_at,
        )
        for v in vaults
    ]
    
    vaults_data.sort(key=lambda b: getattr(b, sort_by))
    
    return {
        "ok": True,
        "vaults": vaults_data
    }
    
@web_vaults.post('/vaults/{vault_id}/unlock')
async def unlock_vault__router(
    vault_id: int,
    vault_master_password: str = Body(...),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
    jwt_service: JWT_Service = Depends(get_jwt_service)
):
    user_id = int(token_data.sub)
    vault_dao = VaultDao(session=db)
    vault = await vault_dao.get_vault_by_field(field=VaultFields.ID, value=int(vault_id), user_id=user_id)
    if not vault:
        raise HTTPException(404, "Wrong vault data")
    
    # Проверить правильный ли master_password с помощью попытки расшифровать пароли
    try:
        kek = derive_key(master_password=vault_master_password, salt_b64=vault.salt)
        dek = decrypt_dek(kek=kek, encrypted_dek=vault.encrypted_dek)
        decrypted_passwords = decrypt_vault_passwords(encrypted_passwords=vault.encrypted_passwords, key=dek)
    except InvalidToken:
        raise HTTPException(401, "Wrong master password")
        
    # Создать токен и добавить его в ответ
    vault_token = await create_token_and_session(
        session=db,
        jwt_service=jwt_service,
        user_id=user_id,
        token_type=SessionType.VAULT
    )
    content = {
        "ok": True,
        "detail": "Vault is successfully unlocked"
    }    
    response = JSONResponse(content=content)
    add_vault_cookie(response=response, jwt_service=jwt_service, value=vault_token.token)
    
    # Сохранить сессию которую созздали
    await db.commit()
    
    return response
    


    
