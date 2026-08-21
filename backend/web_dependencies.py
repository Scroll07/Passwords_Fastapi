from fastapi import Body, HTTPException, Depends, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from cryptography.fernet import InvalidToken

from backend.api_dependencies import get_db, get_jwt_service
from backend.services.cookies import add_bearer_cookie, add_refresh_cookie
from backend.dao.session_dao import SessionDao
from backend.schemas.db_schema import UserFields, SessionType
from backend.dao.userDao import UserDao
from backend.schemas.jwt import JWTDecodedData
from backend.services.jwt_service import JWT_Service, create_token_and_session
from backend.schemas.base import WebChangePasswordSchema
from backend.core.logger import get_logger
from backend.password_manager.services.password import (
    create_user_vault,
    check_is_vault_exists
)
from backend.schemas.requests import RequstVaultDependecie
from backend.dao.vaultDao import VaultDao, VaultFields
from backend.password_manager.core.crypto import (
    derive_key,
    decrypt_dek,
    decrypt_vault_passwords,
    encrypt_vault_passwords
)


logger = get_logger(__name__)

async def _web_try_refresh_token(
    request: Request,
    db: AsyncSession,
    jwt_service: JWT_Service,
) -> JWTDecodedData:
    try:
        refresh_token = request.cookies.get("refresh_token")
        if refresh_token is None:
            raise HTTPException(401, "No bearer token")

        jwt_servise = get_jwt_service()
        refresh_token_data = jwt_servise.verify_token(token=refresh_token)
        await create_token_and_session(
            session=db,
            jwt_service=jwt_service,
            user_id=int(refresh_token_data.sub),
            token_type=SessionType.REFRESH
        )   
        user_dao = UserDao(session=db)
        user = await user_dao.get_user_by_field(field=UserFields.ID, value=int(refresh_token_data.sub))
        if user is None:
            raise HTTPException(401, "Wrong user data")
        if not user.is_active:
            raise HTTPException(401, "This account is not active")
        
        dao = SessionDao(session=db)
        session = await dao.get_session(session_id=refresh_token_data.sid)
        if session is None:
            raise HTTPException(401, "Wrong session id, session does not exists")
        if not session.is_active:
            raise HTTPException(401, "Session was expired, try to login")
    
        if user.id != int(refresh_token_data.sub):
            raise HTTPException(401, "Invalid session binding")
        return refresh_token_data
    except InvalidTokenError as e:
        logger.exception(e)
        raise HTTPException(401, "Wrong refresh token")
    except Exception as e:
        logger.exception(e)
        raise e


async def verify_web_user(
    request: Request,
    response: Response,
    db = Depends(get_db),
    jwt_service = Depends(get_jwt_service)    
) -> JWTDecodedData:
    try:
        bearer_token = request.cookies.get("bearer_token")
        if bearer_token is None:            
            raise HTTPException(401, "No bearer token")
        token_data = jwt_service.verify_token(token=bearer_token)
        user_dao = UserDao(session=db)
        user = await user_dao.get_user_by_field(field=UserFields.ID, value=int(token_data.sub))
        if user is None:
            raise HTTPException(401, "Wrong user data")
        if not user.is_active:
            raise HTTPException(401, "This account is not active")
        
        dao = SessionDao(session=db)
        session = await dao.get_session(session_id=token_data.sid)
        if session is None:
            raise HTTPException(401, "Wrong session id, session does not exists")
        if not session.is_active:
            raise HTTPException(401, "Session was expired, try to login")
    
        if user.id != int(token_data.sub):
            raise HTTPException(401, "Invalid session binding")
    
        return token_data
    
    except ExpiredSignatureError:
        logger.info("Bearer was expired, trying to verify refresh token")
        try:
            refresh_token_data = await _web_try_refresh_token(
                request=request,
                db=db,
                jwt_service=jwt_service
            )
            bearer_token = await create_token_and_session(
                session=db,
                jwt_service=jwt_service,
                user_id=int(refresh_token_data.sub),
                token_type=SessionType.BEARER
            )
            refresh_token = await create_token_and_session(
                session=db,
                jwt_service=jwt_service,
                user_id=int(refresh_token_data.sub),
                token_type=SessionType.REFRESH
            )
            
            add_bearer_cookie(response=response, jwt_service=jwt_service, value=bearer_token.token)
            add_refresh_cookie(response=response, jwt_service=jwt_service, value=refresh_token.token)
        
            await db.commit()
            return refresh_token_data
        except InvalidTokenError as e:
            logger.exception(e)
            raise HTTPException(401, "Wrong refresh token") 
    except InvalidTokenError as e:
        logger.exception(e)
        raise HTTPException(401, "Wrong bearer token")
    except HTTPException as e:
        logger.exception(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    
async def verify_web_refresh_token(
    request: Request,
    db = Depends(get_db)
) -> JWTDecodedData:
    try:
        refresh_token = request.cookies.get("refresh_token")
        if refresh_token is None:
            raise HTTPException(401, "No bearer token")

        jwt_servise = get_jwt_service()
        token_data = jwt_servise.verify_token(token=refresh_token)
        
        user_dao = UserDao(session=db)
        user = await user_dao.get_user_by_field(field=UserFields.ID, value=int(token_data.sub))
        if user is None:
            raise HTTPException(401, "Wrong user data")
        if not user.is_active:
            raise HTTPException(401, "This accaunt is not active")
        
        dao = SessionDao(session=db)
        session = await dao.get_session(session_id=token_data.sid)
        if session is None:
            raise HTTPException(401, "Wrong session id, session does not exists")
        if not session.is_active:
            raise HTTPException(401, "Session was expired, try to login")
    
        if user.id != int(token_data.sub):
            raise HTTPException(401, "Invalid session binding")
    
    
        return token_data
    
    except InvalidTokenError as e:
        logger.exception(e)
        raise HTTPException(401, "Wrong refresh token")
    except HTTPException as e:
        logger.exception(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    
async def web_validate_change_passwords(
    username: str = Body(..., min_length=4, max_length=32),
    current_password: str = Body(..., min_length=4, max_length=32),
    new_password: str = Body(..., min_length=4, max_length=32)
    ) -> WebChangePasswordSchema:
    current_password = current_password.strip()
    new_password = new_password.strip()
    
    if " " in current_password or " " in new_password:
        raise HTTPException(400, "The password must not contain spaces")
    
    if current_password == new_password:
        raise HTTPException(400, "New password can not be the same as old password")
    
    return WebChangePasswordSchema(
        username=username,
        current_password=current_password,
        new_password=new_password
    )
    
    
async def web__check_vault_exists(
    request: Request,
    master_password: str = Body(min_length=1),
    token_data: JWTDecodedData = Depends(verify_web_user),
    db: AsyncSession = Depends(get_db),
):
    # # Получить информацию пользователя (username  и т.д.)
    # user_id = int(token_data.sub)
    # dao = UserDao(session=db)
    # user_data = await dao.get_user_data(user_id=user_id)
    # if not user_data:
    #     raise HTTPException(404, "Wrongg user data")
    
    # Проверить существует ли `vault`
    vault_id = request.path_params.get("vault_id")
    if not vault_id:
        raise HTTPException(400, detail="Wrong uri path")
    user_id = int(token_data.sub)
    vault_dao = VaultDao(session=db)
    vault = await vault_dao.get_vault_by_field(field=VaultFields.ID, value=int(vault_id), user_id=user_id)
    if not vault:
        raise HTTPException(404, "Wrong vault data")
    
    # Проверить правильный ли master_password с помощью попытки расшифровать пароли
    try:
        kek = derive_key(master_password=master_password, salt_b64=vault.salt)
        dek = decrypt_dek(kek=kek, encrypted_dek=vault.encrypted_dek)
        decrypted_passwords = decrypt_vault_passwords(encrypted_passwords=vault.encrypted_passwords, key=dek)
    except InvalidToken:
        raise HTTPException(401, "Wrong master password")
        
    return RequstVaultDependecie(
        # token_data=token_data,
        vault=vault,
        master_password=master_password,
        # username=user_data.username
    )
    
    
async def verify_vault_session(
    request: Request,
    db = Depends(get_db),
    bearer_token_data: JWTDecodedData = Depends(verify_web_user),
    jwt_service = Depends(get_jwt_service)    
) -> JWTDecodedData:
    try:
        vault_token = request.cookies.get("vault_token")
        if vault_token is None:            
            raise HTTPException(401, "No bearer token")
        token_data = jwt_service.verify_token(token=vault_token)
        user_dao = UserDao(session=db)
        user = await user_dao.get_user_by_field(field=UserFields.ID, value=int(token_data.sub))
        if user is None:
            raise HTTPException(401, "Wrong user data")
        if not user.is_active:
            raise HTTPException(401, "This account is not active")
        
        dao = SessionDao(session=db)
        session = await dao.get_session(session_id=token_data.sid)
        if session is None:
            raise HTTPException(401, "Wrong session id, session does not exists")
        if not session.is_active:
            raise HTTPException(401, "Session was expired, try to login")
    
        if user.id != int(token_data.sub):
            raise HTTPException(401, "Invalid session binding")
    
        return token_data
    
    except ExpiredSignatureError:
        logger.info("Vault token was expired")
        raise HTTPException(401, "Vault session was expired")
    except InvalidTokenError as e:
        logger.exception(e)
        raise HTTPException(401, "Wrong bearer token")
    except HTTPException as e:
        logger.exception(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")