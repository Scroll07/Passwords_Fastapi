from fastapi import Header, HTTPException, Depends


from src.core.database import get_db
from src.services.secrets import jwt_service


async def get_token(authorization: str | None = Header(default=None)) -> str:
    if authorization is None:
        raise HTTPException(401, "Missing autrization header")

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0] not in ("Bearer", "Refresh"):
        raise HTTPException(401, "Invalid content of header")
    
    token = parts[1]
    return token

async def verify_user(token = Depends(get_token)):
    ...









