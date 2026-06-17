
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.session_dao import SessionDao
from src.services.jwt_service import JWT_Service, create_token_and_session
from src.dao.role_dao import RoleDAO
from src.schemas.jwt import JWTDecodedData, TokenType
from src.schemas.db_schema import UserFields, UserRoles, CreateUserInDb
from src.schemas.api_responses import LoginResponse, MessageResponse, RefreshResponse
from src.dependincies import get_db, verify_refresh_token, get_jwt_service, verify_user, validate_change_passwords
from src.schemas.base import ChangePasswordSchema, RegisterRequestData, LoginRequest
from src.dao.userDao import UserDao
from src.services.secrets import hash_password, verify_password
from src.core.logger import get_logger

logger = get_logger(__name__)

api_users = APIRouter()

#==============================
#            API   
#==============================
@api_users.post("/register", status_code=201)
async def register_post(
    user_data: RegisterRequestData,
    db: AsyncSession = Depends(get_db),
):
    try:
        user_dao = UserDao(db)

        exist_username = await user_dao.get_user_by_field(
            UserFields.USERNAME, user_data.username
        )
        if exist_username:
            raise HTTPException(409, detail="User with this username alredy exists")

        if user_data.telegram_id is not None:
            exist_telegram_id = await user_dao.get_user_by_field(
            UserFields.TELEGRAM_ID, user_data.telegram_id
        )
            if exist_telegram_id:
                raise HTTPException(409, detail="User with this telegram id alredy exists")

        role_dao = RoleDAO(session=db)
        user_role = await role_dao.get_role(role_name=UserRoles.USER)
        if not user_role:
            logger.error("Cant get user role for register")
            raise HTTPException(500, "Internal server error")

        password_hash = hash_password(user_data.password)
        create_data = CreateUserInDb(
            username=user_data.username,
            password_hash=password_hash,
            telegram_id=user_data.telegram_id
        )
        await user_dao.create_user(user_data=create_data, role_id=user_role.id)
        
        response = MessageResponse(
            ok=True,
            detail="New user was sucessfully created"
        )
        await db.commit()
        return response

    except HTTPException as e:
        logger.warning(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")


@api_users.post("/login")
async def login_post(
    user_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    jwt_service: JWT_Service = Depends(get_jwt_service)
    
):
    try:
        dao = UserDao(db)
        user = await dao.get_user_by_field(UserFields.USERNAME, user_data.username)
        if not user:
            raise HTTPException(401, "Wrong user data")

        if not verify_password(user_data.password, user.password_hash):
            raise HTTPException(401, "Wrong user data")

        bearer_token = await create_token_and_session(
            session=db,
            jwt_service=jwt_service,
            user_id=user.id,
            token_type=TokenType.BEARER
        )
        refresh_token = await create_token_and_session(
            session=db,
            jwt_service=jwt_service,
            user_id=user.id,
            token_type=TokenType.REFRESH
        )
        
        response = LoginResponse(
            ok=True,
            detail="Success login",
            bearer_token=bearer_token,
            refresh_token=refresh_token
        )
        
        await db.commit()
        return response
    
    except HTTPException as e:
        logger.warning(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    
    
@api_users.post("/logout")
async def logout(
    db: AsyncSession = Depends(get_db),
    data: JWTDecodedData = Depends(verify_user)
):    
    session_dao = SessionDao(session=db)

    await session_dao.make_unactive_session(user_id=int(data.sub))
    await db.commit()
    
    return {
        "ok": True,
        "detail": "Logout successful",
    }    

@api_users.get("/refresh")
async def refresh_get(
    data: JWTDecodedData = Depends(verify_refresh_token),
    db: AsyncSession = Depends(get_db),
    jwt_service: JWT_Service = Depends(get_jwt_service)
):
    try:
        bearer_token = await create_token_and_session(
            session=db,
            jwt_service=jwt_service,
            user_id=int(data.sub),
            token_type=TokenType.BEARER
        )
        refresh_token = await create_token_and_session(
            session=db,
            jwt_service=jwt_service,
            user_id=int(data.sub),
            token_type=TokenType.REFRESH
        )
        
        response = RefreshResponse(
            ok=True,
            detail="Tokens were successfully refreshed",
            bearer_token=bearer_token,
            refresh_token=refresh_token
        )
        await db.commit()
        return response
    
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    

@api_users.patch("/change-password")
async def change_password(
    data: ChangePasswordSchema = Depends(validate_change_passwords), 
    user_data = Depends(verify_user),
    db=Depends(get_db),
):
    try:
        dao = UserDao(session=db)
        user = await dao.get_user_by_field(field=UserFields.ID, value=int(user_data.sub))
        if user is None:
            logger.exception(f"User with this user_id={user_data.sub} does not exist")
            raise HTTPException(404, "User with this user_id does not exist")
        
        if not verify_password(password=data.current_password, password_hash=user.password_hash):
            raise HTTPException(401, "Wrong user data")
        
        new_hash = hash_password(password=data.new_password)
        await dao.change_password(user=user, new_hash=new_hash)
        
        response = MessageResponse(
            ok=True,
            detail="Your password was successuflly changed",
        )
        return response
    
    except HTTPException as e:
        logger.exception(e)        
        raise e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
    

