import bcrypt
import jwt
# from jwt.exceptions import 
from datetime import timedelta, datetime, timezone

from src.core.settings import settings as s
from src.schemas.jwt import Token

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"), 
        password_hash.encode("utf-8")
    )
    
    
ALGORITM = "HS256"
TOKEN_EXPIRES_IN = 30

class JWT:
    def __init__(self, algoritm: str, secret_key: str) -> None:
        self.algoritm = algoritm
        self.secret_key = secret_key
        
    def create_access_token(self, user_id: int, expires_in_min: int = TOKEN_EXPIRES_IN) -> Token:
        expires = datetime.now(timezone.utc) + timedelta(minutes=expires_in_min)
        
        encode_to = {
            "user_id": user_id,
            "type": "access",
            "exp": expires,
        }
        encoded = jwt.encode(encode_to, self.secret_key, self.algoritm)
        return Token(access_token=encoded, token_type="bearer")

    def verify_token(self, token: str) -> int | bool:
        try:
            decoded = jwt.decode(token, self.secret_key, [self.algoritm])
        except Exception as e:
            raise e
        

        type = decoded.get("type")
        if type is None:
            raise ValueError("No type")
        
        if type == "access":
            user_id = decoded.get("user_id")
            if user_id is None:
                raise ValueError("Отстутсвует user_id")
            
            return int(user_id)
        
        elif type == "refresh":
            return True
        
        else:
            raise ValueError("Wrong type")
        
        
        
jwt_service = JWT(ALGORITM, s.SECRET_TOKEN_KEY)