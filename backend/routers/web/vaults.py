from fastapi import APIRouter, Body, Request, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import InvalidToken
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from backend.dao.session_dao import SessionDao
from backend.services.jwt_service import JWT_Service
from backend.dao.userDao import UserDao
from backend.schemas.jwt import JWTDecodedData
from backend.schemas.base import SortByVaults, VaultData
from backend.schemas.db_schema import SessionType, UserFields
from backend.schemas.api_responses import MessageResponse
from backend.dependencies import get_db, get_jwt_service
from backend.web_dependencies import verify_web_user, verify_vault_session, web__check_vault_exists
from backend.core.logger import get_logger
from backend.schemas.requests import RequstVaultDependecie
from backend.dao.vaultDao import VaultDao, VaultFields, Vaults
from backend.services.jwt_service import create_token_and_session
from backend.password_manager.services.password import (
    create_user_vault
)
from backend.password_manager.core.crypto import (
    derive_key,
    decrypt_dek,
    decrypt_vault_passwords
)
from backend.services.cookies import add_vault_cookie


logger = get_logger(__name__)

web_vaults = APIRouter()


#Ручка чтобы создать персональный файл с шифрованием

# + добавить функцию чтобы проверять создан ли файл у пользвоателя
# (функция должна быть где-то в services или в dependencies)

# Добавь логи к каждой ручке

# Добавить роутер для скачивания vault file (Но сначала переделай cli)

@web_vaults.post('/vaults/create')
async def create_vault__router(
    vault_name: str = Body(..., max_length=32, min_length=1),
    vault_master_password: str = Body(..., max_length=32, min_length=4),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_data.sub)
    logger.info("Create vault attempt; user_id=%s", user_id)

    try:
        dao = UserDao(session=db)
        user_data = await dao.get_user_data(user_id=user_id)
        if not user_data:
            logger.warning("Wrong user data; user_id=%s", user_id)
            raise HTTPException(404, "Wrong user data")

        vault_name = vault_name.strip()
        vault_dao = VaultDao(session=db)
        vault = await vault_dao.get_vault_by_field(field=VaultFields.NAME, value=vault_name, user_id=user_id)
        if vault:
            logger.warning("Vault name conflict; user_id=%s vault_name=%s", user_id, vault_name)
            raise HTTPException(409, "Vault with such name alredy exists")

        encrypted_data = create_user_vault(master_password=vault_master_password)

        await vault_dao.create_vault(
            user_id=user_id,
            name=vault_name,
            encrypted_passwords=encrypted_data.encrypted_passwords,
            salt=encrypted_data.salt,
            encrypted_dek=encrypted_data.encrypted_dek
        )

        logger.info("Vault created; user_id=%s vault_name=%s", user_id, vault_name)
        return {
            "ok": True,
            "detail": "New vault was successfully created"
        }

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


@web_vaults.delete('/vaults/{vault_id}')
async def delete_vault__router(
    vault_id: int,
    token_data: JWTDecodedData = Depends(verify_web_user),
    vault: Vaults = Depends(web__check_vault_exists),
    vault_data: RequstVaultDependecie = Depends(verify_vault_session),
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
        return {
            "ok": True,
            "detail": "Vault was successfully deleted"
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "Unexpected error while deleting vault; user_id=%s vault_id=%s",
            user_id,
            vault_id,
        )
        raise HTTPException(500, 'Internal server error')


@web_vaults.post('/vaults/{vault_id}/rename')
async def rename_vault__router(
    vault_id: int,
    new_name: str = Body(min_length=1),
    vault_data: RequstVaultDependecie = Depends(verify_vault_session),
    vault: Vaults = Depends(web__check_vault_exists),
    db: AsyncSession = Depends(get_db),
):
    logger.info("Rename vault attempt; vault_id=%s", vault_id)

    try:
        vault.name = new_name.strip()
        await db.commit()

        logger.info("Vault renamed; vault_id=%s", vault_id)
        return {
            "ok": True,
            "detail": "Vault was successfully renamed"
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "Unexpected error while renaming vault; vault_id=%s",
            vault_id,
        )
        raise HTTPException(500, 'Internal server error')


@web_vaults.get('/vaults')
async def get_user_vaults__router(
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
    sort_by: SortByVaults = Query(SortByVaults.CREATED_AT)
):
    user_id = int(token_data.sub)
    logger.info("Get user vaults; user_id=%s sort_by=%s", user_id, sort_by.value)

    try:
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

        logger.info("Vaults fetched; user_id=%s count=%s", user_id, len(vaults_data))
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


@web_vaults.post('/vaults/{vault_id}/unlock')
async def unlock_vault__router(
    vault_id: int,
    vault_master_password: str = Body(..., min_length=4),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
    jwt_service: JWT_Service = Depends(get_jwt_service),

):
    user_id = int(token_data.sub)
    logger.info("Vault unlock attempt; user_id=%s vault_id=%s", user_id, vault_id)

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

        content = {"ok": True, "detail": "Vault is successfully unlocked"}
        response = JSONResponse(content=content)
        add_vault_cookie(response=response, jwt_service=jwt_service, value=vault_token.token)
        await db.commit()

        logger.info("Vault unlocked; user_id=%s vault_id=%s", user_id, vault_id)
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


@web_vaults.post('/vaults/{vault_id}/status')
async def status_vault__router(
    vault_id: int,
    request: Request,
    vault_data: RequstVaultDependecie = Depends(verify_vault_session),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
    jwt_service: JWT_Service = Depends(get_jwt_service)
):
    logger.info("Vault status check; vault_id=%s", vault_id)

    try:
        vault_token = request.cookies.get("vault_token")
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


@web_vaults.get('/vaults/{vault_id}/info')
async def get_vault__router(
    vault_id: int,
    vault: Vaults = Depends(web__check_vault_exists),
    vault_data: RequstVaultDependecie = Depends(verify_vault_session),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_data.sub)
    logger.info("Get vault info; user_id=%s vault_id=%s", user_id, vault_id)

    try:
        vault_response_data = VaultData.model_validate(vault)
        logger.info("Vault info fetched; user_id=%s vault_id=%s", user_id, vault_id)
        return {
            "ok": True,
            "vault": vault_response_data
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "Unexpected error while fetching vault info; user_id=%s vault_id=%s",
            user_id,
            vault_id,
        )
        raise HTTPException(500, "Internal server error")


@web_vaults.post('/vaults/{vault_id}/change-pin')
async def change_pin__router(
    vault_id: int,
    vault: Vaults = Depends(web__check_vault_exists),
    vault_data: RequstVaultDependecie = Depends(verify_vault_session),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
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


@web_vaults.post('/vaults/{vault_id}/download')
async def download_vault__router(
    vault_id: int,
    vault: Vaults = Depends(web__check_vault_exists),
    vault_data: RequstVaultDependecie = Depends(verify_vault_session),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(token_data.sub)
    logger.info("Download vault; user_id=%s vault_id=%s", user_id, vault_id)

    try:
        # Написать download router когда переделаю CLI, потому что непонятно какую структуру файла собирать
        ...

    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "Unexpected error while downloading vault; user_id=%s vault_id=%s",
            user_id,
            vault_id,
        )
        raise HTTPException(500, "Internal server error")
