import bcrypt
import jwt

# from jwt.exceptions import
from datetime import timedelta, datetime, timezone

from src.schemas.jwt import EncodedToken, TokenType, TokenData


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


ALGORITM = "HS256"
TOKEN_EXPIRES_IN_ACCESS = 30
TOKEN_EXPIRES_IN_REFRESH = 7

class JWT:
    def __init__(self, algoritm: str, secret_key: str) -> None:
        self.algoritm = algoritm
        self.secret_key = secret_key

    def create_access_token(
        self, user_id: int, expires_in_min: int = TOKEN_EXPIRES_IN_ACCESS
    ) -> EncodedToken:
        expires = datetime.now(timezone.utc) + timedelta(minutes=expires_in_min)
        
        token_data = TokenData(
                user_id=user_id,
                type=TokenType.BEARER,
                exp=expires
            )

        encoded = jwt.encode(token_data.model_dump(), self.secret_key, self.algoritm)
        return EncodedToken(token=encoded, token_type=TokenType.BEARER)
    
    def create_refresh_token(
        self, user_id: int, expires_in_days: int = TOKEN_EXPIRES_IN_REFRESH
        ) -> EncodedToken:
        expires = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        
        token_data = TokenData(
                user_id=user_id,
                type=TokenType.REFRESH,
                exp=expires
            )       
        encoded = jwt.encode(token_data.model_dump(), self.secret_key, self.algoritm) 
        return EncodedToken(token=encoded, token_type=TokenType.REFRESH)
        
        

    def verify_token(self, token: str) -> int:
        try:
            decoded = jwt.decode(token, self.secret_key, [self.algoritm])
        except Exception as e:
            raise e

        type = decoded.get("type")
        if type is None:
            raise ValueError("No type")

        if type == TokenType.BEARER:
            user_id = decoded.get("user_id")
            if user_id is None:
                raise ValueError("Отстутсвует user_id")

            return int(user_id)

        elif type == TokenType.REFRESH:
            user_id = decoded.get("user_id")
            if user_id is None:
                raise ValueError("Отстутсвует user_id")
            
            return int(user_id)
            
        else:
            raise ValueError("Wrong type")



