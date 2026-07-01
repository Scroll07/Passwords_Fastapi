from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from src.schemas.jinja_context import UserBackupContext
from src.dependincies import get_jwt_service, verify_web_user, get_db
from src.core.templates import templates
from src.core.logger import get_logger
from src.schemas.base import BackupData
from src.dao.backupDao import BackupDao


logger = get_logger(name="Static pages")

pages = APIRouter()

# Home
# Product
# How It Works
# Pricing
# FAQ
# Docs


@pages.get(path="/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html"
    )
    
@pages.get(path="/web/product", response_class=HTMLResponse)
async def product(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="product.html"
    )

@pages.get(path="/web/how_it_works", response_class=HTMLResponse)
async def how_it_works(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="how_it_works.html"
    )

@pages.get(path="/web/pricing", response_class=HTMLResponse)
async def pricing(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pricing.html"
    )
    
@pages.get(path="/web/security", response_class=HTMLResponse)
async def security(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="security.html"
    )

@pages.get(path="/web/faq", response_class=HTMLResponse)
async def faq(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="faq.html"
    )

@pages.get(path="/web/docs", response_class=HTMLResponse)
async def docs(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="docs.html"
    )
    
@pages.get(path="/web/login", response_class=HTMLResponse)
async def login(request: Request):
    bearer_token = request.cookies.get("bearer_token")
    try:
        if bearer_token:
            jwt_service = get_jwt_service()
            if jwt_service.verify_token(token=bearer_token):
                return RedirectResponse("/web/dashboard")
    finally:    
        return templates.TemplateResponse(
            request=request,
            name="login.html"
        )
    
@pages.get(path="/web/forgot-password", response_class=HTMLResponse)
async def forgot_password(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html"
    )
    
@pages.get(path="/web/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )

@pages.get(path="/web/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    token_data = Depends(verify_web_user),
    db = Depends(get_db)
    
):
    try:
        dao = BackupDao(session=db)
        user_backups = await dao.get_user_backups(user_id=int(token_data.sub))
        context = [BackupData(
            id=b.id,
            name=b.name,
            rows=b.rows,
            pinned=b.pinned,
            created_at=b.created_at
            ).model_dump() for b in user_backups]

        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={"backups": context}
        )
    except Exception as e:
        logger.exception(e)
        
@pages.get(path="/web/backups/{backup_id}", response_class=HTMLResponse)
async def user_backup(
    request: Request,
    backup_id: int,
    token_data = Depends(verify_web_user),
    db = Depends(get_db) 
):
    try:
        dao = BackupDao(session=db)
        backup = await dao.get_backup_by_id(user_id=int(token_data.sub), backup_id=backup_id)
        if not backup:
            raise HTTPException(400, "You do not have backup with such id")
        
        context = BackupData(
            id=backup.id,
            name=backup.name,
            rows=backup.rows,
            pinned=backup.pinned,
            created_at=backup.created_at
        )
        
        return templates.TemplateResponse(
            request=request,
            name="user_backup.html",
            context={"backup": context.model_dump()}
        )
    except HTTPException as e:
        logger.exception(e)
        return templates.TemplateResponse(
                request=request,
                name="user_backup.html",
                context=UserBackupContext(
                    error=e.detail
                ).model_dump()
            )
    
    except Exception as e:
        logger.exception(e)
        return templates.TemplateResponse(
                request=request,
                name="user_backup.html",
                context=UserBackupContext(
                    error="Internal server error"
                ).model_dump()
            )