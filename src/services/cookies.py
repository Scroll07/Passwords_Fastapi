


from datetime import datetime, timedelta, timezone

from fastapi.responses import JSONResponse


def add_cookie(response: JSONResponse, key: str, value: str, expires: datetime) -> None:
    response.set_cookie(
        key=key,
        value=value,
        expires=expires,
        secure=False,       #No https yet
        samesite="lax",
        httponly=True
    )
    
def add_bearer_cookie(response: JSONResponse, value: str) -> None:
    expires = datetime.now(timezone.utc) + timedelta(hours=1)
    add_cookie(
        response=response,
        key="bearer_token",
        value=value,
        expires=expires
    )
    

def add_refresh_cookie(response: JSONResponse, value: str) -> None:
    expires = datetime.now(timezone.utc) + timedelta(days=7)
    add_cookie(
        response=response,
        key="refresh_token",
        value=value,
        expires=expires
    )