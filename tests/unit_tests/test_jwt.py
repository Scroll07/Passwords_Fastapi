from datetime import datetime, timezone, timedelta
import jwt

from src.services.jwt_service import JWT_Service
from src.schemas.jwt import JWTDecodedData, TokenType



def test_create_access_token__returns_token(access_token: str):
    assert access_token
    assert type(access_token) == str
    assert len(access_token.split(".")) == 3

def test_create_access_token__payload_has_sub_sid_exp_type(jwt_service: JWT_Service):
    expires = datetime.now() + timedelta(minutes=15)
    data = JWTDecodedData(
        sub="user_id",
        sid=0,
        exp=int(expires.timestamp()),
        type=TokenType.BEARER
    )
    token = jwt_service.create_access_token(data=data)
    decoded = jwt.decode(token.token, options={"verify_signature": False})
    
    assert decoded.get("sub") == "user_id"
    assert decoded.get("sid") == 0
    assert decoded.get("exp") == int(expires.timestamp())
    assert decoded.get("type") == TokenType.BEARER
    
def test_verify_token__valid_token__returns_data(jwt_service: JWT_Service):
    expires = datetime.now() + timedelta(minutes=15)
    data = JWTDecodedData(
        sub="user_id",
        sid=0,
        exp=int(expires.timestamp()),
        type=TokenType.BEARER
    )
    token = jwt_service.create_access_token(data=data)
    decoded = jwt_service.verify_token(token=token.token)
    assert data == decoded

    

