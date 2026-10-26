import base64
import datetime
import json

from fastapi import APIRouter, Body, Request, Depends, HTTPException, Query, Response, status
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import InvalidToken
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from backend.core.logger import get_logger
from backend.api_dependencies import (
    verify_user,
    get_db,
    api__check_vault_exists,
    verify_vault_session
)
from backend.dao.session_dao import SessionDao
from backend.dependencies import get_jwt_service
from backend.models.model import Vaults
from backend.password_manager.core.config import TEMPORARY_FILES
from backend.password_manager.services.password import create_user_vault
from backend.schemas.api import (
    CreateVaultDataRequest, 
    CreateVaultResponse, 
    DeleteVaultResponse, 
    MessageResponse, 
    PullRequestData, 
    PullResponse, 
    PullStatuses, 
    PushResponse, 
    PushStatuses, 
    RenameVaultResponse, 
    SortByVaults, 
    UnlockVault, 
    PushRequestData
)
from backend.schemas.db_schema import SessionType, UserFields
from backend.schemas.jwt import EncodedToken, JWTDecodedData
from backend.dao.userDao import UserDao
from backend.dao.vaultDao import VaultDao, VaultFields
from backend.password_manager.core.crypto import (
    derive_key,
    decrypt_dek,
    decrypt_vault_passwords
)
from backend.schemas.vaults import EncryptedUserVault, VaultData
from backend.services.jwt_service import JWT_Service, create_token_and_session



class RequstVaultDependecie(BaseModel):
    vault: Vaults
    dek: bytes
    
    model_config = ConfigDict(arbitrary_types_allowed=True)




logger = get_logger(__name__)

api_vaults = APIRouter()


#Ручка чтобы создать персональный файл с шифрованием

# + добавить функцию чтобы проверять создан ли файл у пользвоателя
# (функция должна быть где-то в services или в dependencies)

# Добавь логи к каждой ручке

# Добавить роутер для скачивания vault file (Но сначала переделай cli)

@api_vaults.post('/vaults/create', status_code=201)
async def create_vault__router(
    payload: CreateVaultDataRequest,
    token_data: JWTDecodedData = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
):

    user_id = int(token_data.sub)
    vault_name = payload.name
    
    logger.info("Create vault attempt; user_id=%s", user_id)
    try:
        vault_dao = VaultDao(session=db)
        vault = await vault_dao.get_vault_by_field(field=VaultFields.NAME, value=vault_name, user_id=user_id)
        if vault is not None:
            raise HTTPException(409, "Vault with this name already exists")
        
        encrypted_dek_bytes = base64.b64decode(payload.encrypted_dek) 
        new_vault = await vault_dao.create_vault(
            user_id=user_id,
            name=vault_name,
            encrypted_passwords='',
            salt=payload.salt,
            encrypted_dek=encrypted_dek_bytes
        )

        return CreateVaultResponse(
            ok=True,
            detail="New vault was successfully created",
            vault_id=new_vault.id
        )

    except ValidationError as e:
        logger.warning("Vault creation validation error; user_id=%s", user_id)
        raise HTTPException(401, e.errors()[0]["msg"])
    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "Unexpected error while creating vault; user_id=%s",
            user_id,
        )
        raise HTTPException(500, 'Internal server error')


@api_vaults.get('/vaults')
async def get_user_vaults__router(
    vault_id: int | None = Query(None),
    token_data: JWTDecodedData = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
    sort_by: SortByVaults = Query(SortByVaults.CREATED_AT),
):
    user_id = int(token_data.sub)
    dao = VaultDao(session=db)

    try:
        vaults = await dao.get_user_vaults(user_id=user_id)

        vaults_data = [
            VaultData(
                id=v.id,
                name=v.name,
                entries=v.entries,
                pinned=v.pinned,
                version=v.version,
                created_at=v.created_at,
                updated_at=v.updated_at
            )
            for v in vaults
        ]

        vaults_data.sort(key=lambda b: getattr(b, sort_by))

        return {
            "ok": True,
            "vaults": vaults_data
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "Unexpected error while fetching user vaults; user_id=%s",
            user_id,
        )
        raise HTTPException(500, 'Internal server error')
    
@api_vaults.get('/vaults/{vault_id}')
async def get_user_vault__router(
    vault_id: int,
    token_data: JWTDecodedData = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_data.sub)

    try:
        dao = VaultDao(session=db)
        vault = await dao.get_vault_by_field(field=VaultFields.ID, value= vault_id, user_id=user_id)

        vault_data = VaultData.model_validate(vault)

        return {
            "ok": True,
            "vault": vault_data
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "Unexpected error while fetching user vault; user_id=%s",
            user_id,
        )
        raise HTTPException(500, 'Internal server error')

@api_vaults.delete('/vaults/{vault_id}')
async def delete_vault__router(
    vault_id: int,
    token_data: JWTDecodedData = Depends(verify_user),
    vault: Vaults = Depends(api__check_vault_exists),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_data.sub)
    logger.info("Delete vault attempt; user_id=%s vault_id=%s", user_id, vault_id)

    try:
        vault_dao = VaultDao(session=db)
        deleted_vault = await vault_dao.delete_vault(user_id=user_id, vault_id=vault_id)
        if not deleted_vault:
            logger.warning("Wrong vault data on delete; user_id=%s vault_id=%s", user_id, vault_id)
            raise HTTPException(401, "Wrong vault data")

        logger.info("Vault deleted; user_id=%s vault_id=%s", user_id, vault_id)
        
        return DeleteVaultResponse(
            ok=True,
            detail="Vault was successfully deleted",
            vault_id=vault.id,
            vault_name=vault.name
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "Unexpected error while deleting vault; user_id=%s vault_id=%s",
            user_id,
            vault_id,
        )
        raise HTTPException(500, 'Internal server error')


@api_vaults.post('/vaults/{vault_id}/rename')
async def rename_vault__router(
    vault_id: int,
    new_name: str = Body(min_length=1),
    vault: Vaults = Depends(api__check_vault_exists),
    db: AsyncSession = Depends(get_db),
    vault_data: RequstVaultDependecie = Depends(verify_vault_session)
):
    logger.info("Rename vault attempt; vault_id=%s", vault_id)

    try:
        old_name = vault.name
        vault.name = new_name.strip()
        vault.version += 1
        await db.commit()

        logger.info("Vault renamed; vault_id=%s", vault_id)
        
        return RenameVaultResponse(
            ok=True,
            detail="Vault was successfully renamed",
            vault_id=vault.id,
            old_vault_name=old_name,
            new_vault_name=new_name
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "Unexpected error while renaming vault; vault_id=%s",
            vault_id,
        )
        raise HTTPException(500, 'Internal server error')


@api_vaults.post('/vaults/{vault_id}/change-pin')
async def change_pin__router(
    vault_id: int,
    vault: Vaults = Depends(api__check_vault_exists),
    token_data: JWTDecodedData = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
    vault_data: RequstVaultDependecie = Depends(verify_vault_session)
):
    user_id = int(token_data.sub)
    logger.info("Change vault pin; user_id=%s vault_id=%s", user_id, vault_id)

    try:
        vault.pinned = not vault.pinned
        await db.commit()

        action = "pinned" if vault.pinned else "unpinned"
        logger.info("Vault pin changed; user_id=%s vault_id=%s pinned=%s", user_id, vault_id, vault.pinned)
        return {
            "ok": True,
            "detail": f"Your vault was successfully {action}"
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "Unexpected error while changing vault pin; user_id=%s vault_id=%s",
            user_id,
            vault_id,
        )
        raise HTTPException(500, "Internal server error")
    
    
@api_vaults.post('/vaults/{vault_id}/download')
async def download_vault__router(
    vault_id: int,
    vault: Vaults = Depends(api__check_vault_exists),
    token_data: JWTDecodedData = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
    vault_data: RequstVaultDependecie = Depends(verify_vault_session)
):
    user_id = int(token_data.sub)
    logger.info("Download vault; user_id=%s vault_id=%s", user_id, vault_id)

    try:
        # Написать download router когда переделаю CLI, потому что непонятно какую структуру файла собирать
        
        vault_dao = VaultDao(session=db)
        encrypted_vault_data = await vault_dao.get_encrypted_vault_data(user_id=user_id, vault_id=vault.id)
        if encrypted_vault_data is None:
            raise HTTPException(404, detail="You have no vault with such id")
        
        content = encrypted_vault_data.model_dump_json(indent=4)
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
        filename = f"{encrypted_vault_data.name}_{date}.json"
            
        return Response(
            content=content,
            media_type='application/json',
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

    except HTTPException as e:
        raise e
    except Exception:
        logger.exception(
            "Unexpected error while downloading vault; user_id=%s vault_id=%s",
            user_id,
            vault_id,
        )
        raise HTTPException(500, "Internal server error")
        

@api_vaults.post('/vaults/{vault_id}/status')
async def status_vault__router(
    vault_id: int,
    request: Request,
    vault_data: RequstVaultDependecie = Depends(verify_vault_session),
    token_data: JWTDecodedData = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
    jwt_service: JWT_Service = Depends(get_jwt_service)
):
    logger.info("Vault status check; vault_id=%s", vault_id)

    try:
        vault_token = request.headers.get("Vault")
        if vault_token is None:
            logger.warning("No vault token in status check; vault_id=%s", vault_id)
            raise HTTPException(401, "No vault token")
        token_data = jwt_service.verify_token(token=vault_token)
        user_id = int(token_data.sub)
        user_dao = UserDao(session=db)
        user = await user_dao.get_user_by_field(field=UserFields.ID, value=user_id)
        if user is None:
            logger.warning("Wrong user data in status check; user_id=%s", user_id)
            raise HTTPException(401, "Wrong user data")
        if user.id != user_id:
            logger.warning("Invalid session binding in status check; user_id=%s", user_id)
            raise HTTPException(401, "Invalid session binding")
        if not user.is_active:
            logger.warning("Account not active in status check; user_id=%s", user_id)
            raise HTTPException(401, "This account is not active")

        dao = SessionDao(session=db)
        session = await dao.get_session(session_id=token_data.sid)
        if session is None:
            logger.warning("Session does not exist in status check; sid=%s", token_data.sid)
            raise HTTPException(401, "Wrong session id, session does not exists")
        if not session.is_active:
            logger.warning("Session expired in status check; sid=%s", token_data.sid)
            raise HTTPException(401, "Session was expired")

        if session.vault_id != vault_id:
            logger.warning("No vault access in status check; user_id=%s vault_id=%s", user_id, vault_id)
            raise HTTPException(401, "You have no access to this vault. Wrong vault id")

        logger.info("Vault status active; vault_id=%s", vault_id)
        return MessageResponse(
            ok=True,
            detail="Session is active",
        )

    except ExpiredSignatureError:
        logger.info("Vault token expired; vault_id=%s", vault_id)
        raise HTTPException(status_code=400, detail="Vault token was expired")
    except InvalidTokenError:
        logger.warning("Wrong vault token in status check; vault_id=%s", vault_id)
        raise HTTPException(400, detail="Wrong vault token")
    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "Unexpected error in vault status check; vault_id=%s",
            vault_id,
        )
        raise HTTPException(500, "Internal server error")




@api_vaults.post('/vaults/{vault_id}/unlock')
async def unlock_vault__router(
    vault_id: int,
    vault_master_password: str = Body(..., min_length=4),
    token_data: JWTDecodedData = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
    jwt_service: JWT_Service = Depends(get_jwt_service),

):
    user_id = int(token_data.sub)

    try:
        vault_dao = VaultDao(session=db)
        vault = await vault_dao.get_vault_by_field(field=VaultFields.ID, value=int(vault_id), user_id=user_id)
        if not vault:
            logger.warning("Wrong vault data on unlock; user_id=%s vault_id=%s", user_id, vault_id)
            raise HTTPException(404, "Wrong vault data")

        try:
            kek = derive_key(master_password=vault_master_password, salt_b64=vault.salt)
            dek = decrypt_dek(kek=kek, encrypted_dek=vault.encrypted_dek)
            decrypt_vault_passwords(encrypted_passwords=vault.encrypted_passwords, key=dek)
        except InvalidToken:
            logger.warning("Wrong master password on unlock; user_id=%s vault_id=%s", user_id, vault_id)
            raise HTTPException(401, "Wrong master password")

        vault_token = await create_token_and_session(
            session=db,
            jwt_service=jwt_service,
            user_id=user_id,
            token_type=SessionType.VAULT,
            vault_id=vault.id,
            dek=dek
        )

        response = UnlockVault(
            ok=True,
            vault_token=vault_token.token,
            detail="Vault is successfully unlocked"
        )
        await db.commit()

        return response

    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "Unexpected error while unlocking vault; user_id=%s vault_id=%s",
            user_id,
            vault_id,
        )
        raise HTTPException(500, 'Internal server error')



@api_vaults.post('/vaults/push', response_model=PushResponse)
async def push_vault(
    payload: PushRequestData,
    response: Response,
    token_data: JWTDecodedData = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_data.sub)
    vault_id = payload.id
    
    vault_dao = VaultDao(session=db)
    if vault_id is None:
        # Значит пушим в первый раз значит надо создать новый vault
        # Но перед этим проверим что у пользователя нет vault с этим именем
        vault_name = payload.name
        vault = await vault_dao.get_vault_by_field(field=VaultFields.NAME, value=vault_name, user_id=user_id)
        if vault is not None:
            raise HTTPException(409, "Pushing this vault first time, but you have existing vault with such name")
        
        encrypted_dek_bytes = base64.b64decode(payload.encrypted_dek) 
        new_vault = await vault_dao.create_vault(
            user_id=user_id,
            name=vault_name,
            encrypted_passwords=payload.encrypted_passwords,
            salt=payload.salt,
            encrypted_dek=encrypted_dek_bytes
        )
        
        return PushResponse(
            ok=True,
            detail="Vault was successfully created and pushed",
            vault_id=new_vault.id,
            status=PushStatuses.CREATED
        )
        
    else:
        vault = await vault_dao.get_vault_by_field(field=VaultFields.ID, value=vault_id, user_id=user_id)
        if vault is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return PushResponse(
                ok=False,
                detail="Vault not found",
                vault_id=vault_id,
                status=PushStatuses.NOT_FOUND
            )

        if not payload.force:
            if payload.version == vault.version:
                return PushResponse(
                    ok=True,
                    detail="Vault already up to date",
                    vault_id=vault_id,
                    status=PushStatuses.UP_TO_DATE
                )
            elif payload.version < vault.version:
                response.status_code = status.HTTP_409_CONFLICT
                return PushResponse(
                    ok=False,
                    detail="Server has higher vault version, use force=True to push",
                    vault_id=vault_id,
                    status=PushStatuses.OUTDATED
                )
                
        vault.name = payload.name
        vault.encrypted_passwords = payload.encrypted_passwords
        vault.version = payload.version
        vault.entries = payload.entries

        await db.commit()
    
    return PushResponse(
        ok=True,
        status=PushStatuses.PUSHED,
        vault_id=vault_id,
        detail="Vault data was succusfully pushed"
    )

@api_vaults.post('/vaults/pull', response_model=PullResponse)
async def pull_vault(
    payload: PullRequestData,
    response: Response,
    token_data: JWTDecodedData = Depends(verify_user),
    db: AsyncSession = Depends(get_db),
    
):
    user_id = int(token_data.sub)
    vault_id = payload.vault_id
    vault_dao = VaultDao(session=db)
    vault = await vault_dao.get_vault_by_field(field=VaultFields.ID, value=vault_id, user_id=user_id)
    if vault is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return PullResponse(
            ok=False,
            detail="Vault not found",
            status=PullStatuses.NOT_FOUND
        )
    
    if payload.version is None:
        payload.force = True

    if not payload.force:
        assert type(payload.version) == int
        if payload.version == vault.version:
            return PullResponse(
                ok=True,
                detail="Vault already up to date",
                status=PullStatuses.UP_TO_DATE
            )
        elif payload.version > vault.version:
            response.status_code = status.HTTP_409_CONFLICT
            return PullResponse(
                ok=False,
                detail="Server has lower vault version, push firstly",
                status=PullStatuses.LOCAL_AHEAD
            )
    
    content = EncryptedUserVault.model_validate(vault, strict=False)
    
    return PullResponse(
        ok=True,
        detail="Successful pull request",
        vault_data=content,
        status=PullStatuses.PULLED
    )


# @api_vaults.post('/vaults/{vault_id}/sync')
# async def sync_vault(
    # Данные которые которые должны получить от клиента:
    #   - base_version: int - версия от которой он делает изменения
    #   - current_version: int - текущая версия до которой он дошел
    #   - 
    
    
    
    
    
    
# ):
    # 3 Варианта, сначала сравнниваем версии vaults: одну от пользователя, вторую - из бд:
        # - Клиентская версия ниже чем в бд: в таком случае данные encrypted_vault в ответе на клиент (на клиенте обновляем vault данными из ответа)
        # - Клиентска и в бд версии совпадают: возвращаем MessageResponse типа все хорошо
        # - Клиенская версия выше чем в бд: это и так ручка /vaults/vaullt_id/sync тут надо либо еще одну ручку создавать либо
        #   делать необязательные параметры encrypted_vault  
        
        
        
        
        

    
    
    
    
    
    