from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from src.dao.session_dao import SessionDao
from src.schemas.jwt import EncodedToken
from src.schemas.jwt import JWTDecodedData, EncodedToken, TokenType
from src.core.settings import get_settings

class JWT_Service:
    def __init__(
        self,
        secret_key: str,
        algoritm: str,
        access_token_expire_in_min: int,
        refresh_token_expire_in_days: int
    ) -> None:
        self.secret_key = secret_key
        self.algoritm = algoritm
        self.access_expire = access_token_expire_in_min
        self.refresh_expire = refresh_token_expire_in_days
        
    def create_access_token(self, data: JWTDecodedData) -> EncodedToken:
        encoded = jwt.encode(data.model_dump(), self.secret_key, self.algoritm)
        return EncodedToken(token=encoded)
    

    def create_refresh_token(
        self,
        data: JWTDecodedData 
        ) -> EncodedToken:
        
        encoded = jwt.encode(data.model_dump(), self.secret_key, self.algoritm) 
        return EncodedToken(token=encoded)
        

    def verify_token(self, token: str) -> JWTDecodedData:
        try:
            decoded = jwt.decode(token, self.secret_key, [self.algoritm])
        except Exception as e:
            raise e
        return JWTDecodedData.model_validate(decoded)


    
async def create_token_and_session(
    session: AsyncSession,
    jwt_service: JWT_Service,
    user_id: int,
    token_type: TokenType
        ) -> EncodedToken:
    session_dao = SessionDao(session=session)
    if token_type == TokenType.BEARER:
        expires = datetime.now(timezone.utc) + timedelta(minutes=jwt_service.access_expire)
        exp_timestamp = int(expires.timestamp())
        user_session = await session_dao.create_session(user_id=user_id, expires_at=expires)
        token_data = JWTDecodedData(
            sub=str(user_id),
            sid=user_session.id,
            exp=exp_timestamp,
            type=TokenType.BEARER
        )
        bearer_token = jwt_service.create_access_token(data=token_data)
        return bearer_token
    elif token_type == TokenType.REFRESH:
        expires = datetime.now(timezone.utc) + timedelta(days=jwt_service.refresh_expire)
        exp_timestamp = int(expires.timestamp())
        user_session = await session_dao.create_session(user_id=user_id, expires_at=expires)
        token_data = JWTDecodedData(
            sub=str(user_id),
            sid=user_session.id,
            exp=exp_timestamp,
            type=TokenType.REFRESH
        )
        refresh_token = jwt_service.create_refresh_token(data=token_data)
        return refresh_token
    else:
        raise ValueError("Wrong token type")
        
    
                