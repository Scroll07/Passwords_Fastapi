from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from backend.dao.session_dao import SessionDao
from backend.schemas.jwt import (
    EncodedToken,
    JWTDecodedData,
    VaultDecodedData
)
from backend.schemas.db_schema import SessionType
from backend.services.secrets import DekFernet

class JWT_Service:
    def __init__(
        self,
        secret_key: str,
        algoritm: str,
        access_token_expire_in_min: int,
        refresh_token_expire_in_days: int,
        vault_token_expire_in_mins: int
    ) -> None:
        self.secret_key = secret_key
        self.algoritm = algoritm
        self.access_expire = access_token_expire_in_min
        self.refresh_expire = refresh_token_expire_in_days
        self.vault_expire = vault_token_expire_in_mins
        
    def create_token(self, data: JWTDecodedData | VaultDecodedData) -> EncodedToken:
        encoded = jwt.encode(data.model_dump(), self.secret_key, self.algoritm)
        return EncodedToken(token=encoded)    
    
    def verify_token(self, token: str) -> JWTDecodedData:
        try:
            decoded = jwt.decode(token, self.secret_key, [self.algoritm])
        except Exception as e:
            raise e
        return JWTDecodedData.model_validate(decoded)
    
    def verify_vault_token(self, token: str) -> VaultDecodedData:
        try:
            decoded = jwt.decode(token, self.secret_key, [self.algoritm])
        except Exception as e:
            raise e
        return VaultDecodedData.model_validate(decoded)
    
    def create_vault_token_data(
        self,
        user_id: int,
        vault_session_id: int,
        expires: datetime,
        dek: bytes,
    ) -> VaultDecodedData:
        expires = datetime.now(timezone.utc) + timedelta(minutes=self.vault_expire)
        exp_timestamp = int(expires.timestamp())
        dek_fernet = DekFernet()
        encrypted_dek_str = dek_fernet.encrypt_dek(dek=dek)
        token_data = VaultDecodedData(
            sub=str(user_id),
            sid=vault_session_id,
            exp=exp_timestamp,
            encrypted_dek=encrypted_dek_str,
            type=SessionType.VAULT
        )
        return token_data
        

    
async def create_token_and_session(
    session: AsyncSession,
    jwt_service: JWT_Service,
    user_id: int,
    token_type: SessionType,
    vault_id: int | None = None,
    dek: bytes | None = None
        ) -> EncodedToken:
    session_dao = SessionDao(session=session)
    if token_type == SessionType.BEARER:
        expires = datetime.now(timezone.utc) + timedelta(minutes=jwt_service.access_expire)
        exp_timestamp = int(expires.timestamp())
        user_session = await session_dao.create_session(user_id=user_id, expires_at=expires, type=SessionType.BEARER)
        token_data = JWTDecodedData(
            sub=str(user_id),
            sid=user_session.id,
            exp=exp_timestamp,
            type=SessionType.BEARER
        )
        bearer_token = jwt_service.create_token(data=token_data)
        return bearer_token
    elif token_type == SessionType.REFRESH:
        expires = datetime.now(timezone.utc) + timedelta(days=jwt_service.refresh_expire)
        exp_timestamp = int(expires.timestamp())
        user_session = await session_dao.create_session(user_id=user_id, expires_at=expires, type=SessionType.REFRESH)
        token_data = JWTDecodedData(
            sub=str(user_id),
            sid=user_session.id,
            exp=exp_timestamp,
            type=SessionType.REFRESH
        )
        refresh_token = jwt_service.create_token(data=token_data)
        return refresh_token
    elif token_type == SessionType.VAULT:
        if vault_id is None or dek is None:
            raise ValueError("Vault id and dek must not be None")
        expires = datetime.now(timezone.utc) + timedelta(minutes=jwt_service.vault_expire)
        vault_session = await session_dao.create_session(user_id=user_id, expires_at=expires, type=SessionType.VAULT, vault_id=vault_id)
        token_data = jwt_service.create_vault_token_data(
            user_id=user_id,
            vault_session_id=vault_session.id,
            expires=expires,
            dek=dek
        )
        vault_token = jwt_service.create_token(data=token_data)
        return vault_token
    else:
        raise ValueError("Wrong token type")
        
    
                