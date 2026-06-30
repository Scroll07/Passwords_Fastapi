from fastapi import APIRouter, Body, Depends, Form, HTTPException, Request, Query
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.templates import templates
from src.dao.session_dao import SessionDao
from src.schemas.jwt import JWTDecodedData, TokenType
from src.services.jwt_service import JWT_Service, create_token_and_session
from src.dao.role_dao import RoleDAO
from src.schemas.api_responses import RedirectPaths, MessageResponse, RefreshResponse
from src.dependincies import get_db, get_jwt_service, verify_web_user, verify_web_refresh_token, web_validate_change_passwords
from src.schemas.base import RegisterRequestData, LoginRequest, WebChangePasswordSchema
from src.schemas.db_schema import UserFields, UserRoles, CreateUserInDb
from src.dao.userDao import UserDao
from src.services.secrets import hash_password, verify_password
from src.core.logger import get_logger
from src.services.cookies import add_bearer_cookie, add_refresh_cookie

logger = get_logger(__name__)

web_users = APIRouter()


#==============================
#            WEB    
#==============================

@web_users.post("/register", status_code=201)
async def web_register_post(
    user_data: RegisterRequestData,
    db=Depends(get_db),
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


@web_users.post("/login", response_class=RedirectResponse)
async def web_login_post(
    request: Request,
    username: str = Form(..., min_length=4, max_length=32),
    password: str = Form(..., min_length=4, max_length=32),
    db=Depends(get_db),
    jwt_service: JWT_Service = Depends(get_jwt_service),
    next: RedirectPaths = Query(RedirectPaths.DASHBOARD)
):
    try:
        dao = UserDao(db)
        user = await dao.get_user_by_field(UserFields.USERNAME, username)
        if not user:
            raise HTTPException(401, "Wrong user data")

        if not verify_password(password, user.password_hash):
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
        
        response = RedirectResponse(
            url=f"/web/{next}",
            status_code=303
        )
        add_bearer_cookie(response=response, value=bearer_token.token)
        add_refresh_cookie(response=response, value=refresh_token.token)
        
        await db.commit()
            
        return response
    
    except HTTPException as e:
        logger.warning(e)
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": e.detail,
                "form_data": {
                    "username": username,
                    "password": password
                }
            }
        )
        
    except Exception as e:
        logger.exception(e)
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Internal server error",
                "form_data": {
                    "username": username,
                    "password": password
                }
            }
        )
    
    
@web_users.post("/logout")
async def web_logout(
    db: AsyncSession = Depends(get_db),
    data: JWTDecodedData = Depends(verify_web_user)
):    
    session_dao = SessionDao(session=db)

    await session_dao.make_unactive_session(user_id=int(data.sub))
    response = RedirectResponse(
        url="/web/login",
        status_code=303
        )
    response.delete_cookie(key="bearer_token", httponly=True, samesite="lax")
    response.delete_cookie(key="refresh_token", httponly=True, samesite="lax")
    
    await db.commit()
    return response
    
    
    
@web_users.patch("/change-password")
async def web_change_password(
    data: WebChangePasswordSchema = Depends(web_validate_change_passwords), 
    db=Depends(get_db),
):
    try:
        dao = UserDao(session=db)
        user = await dao.get_user_by_field(field=UserFields.USERNAME, value=data.username)
        if user is None:
            logger.exception(f"User with this user_id={data.username} does not exist")
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
    
    
    
@web_users.get("/refresh")
async def web_refresh_get(
    token_data: JWTDecodedData = Depends(verify_web_refresh_token),
    db=Depends(get_db),
    jwt_service: JWT_Service = Depends(get_jwt_service),
):
    try:
        bearer_token = await create_token_and_session(
            session=db,
            jwt_service=jwt_service,
            user_id=int(token_data.sub),
            token_type=TokenType.BEARER
        )
        refresh_token = await create_token_and_session(
            session=db,
            jwt_service=jwt_service,
            user_id=int(token_data.sub),
            token_type=TokenType.REFRESH
        )
        
        content = {
            "ok": True,
            "detail": "Tokens were successully refreshed"
        } 
        
        response = JSONResponse(
            content=content
        )
        add_bearer_cookie(response=response, value=bearer_token.token)
        add_refresh_cookie(response=response, value=refresh_token.token)
        
        await db.commit()
        return response
    
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, "Internal server error")
        