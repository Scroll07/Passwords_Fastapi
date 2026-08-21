from datetime import datetime, timedelta, timezone
from fastapi.responses import Response

from backend.services.jwt_service import JWT_Service




def add_cookie(response: Response, key: str, value: str, expires: datetime) -> None:
    response.set_cookie(
        key=key,
        value=value,
        expires=expires,
        secure=False,       #No https yet
        samesite="lax",
        httponly=True
    )
    
def add_bearer_cookie(response: Response, jwt_service: JWT_Service, value: str) -> None:
    expires = datetime.now(timezone.utc) + timedelta(minutes=jwt_service.access_expire)
    add_cookie(
        response=response,
        key="bearer_token",
        value=value,
        expires=expires
    )
    

def add_refresh_cookie(response: Response, jwt_service: JWT_Service, value: str) -> None:
    expires = datetime.now(timezone.utc) + timedelta(days=jwt_service.refresh_expire)
    add_cookie(
        response=response,
        key="refresh_token",
        value=value,
        expires=expires
    )
    
def add_vault_cookie(response: Response, jwt_service: JWT_Service, value: str) -> None:
    expires = datetime.now(timezone.utc) + timedelta(minutes=jwt_service.vault_expire)
    add_cookie(
        response=response,
        key="vault_token",
        value=value,
        expires=expires
    )