from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

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
    if bearer_token:
        jwt_service = get_jwt_service()
        if jwt_service.verify_token(token=bearer_token):
            return RedirectResponse("/web/dashboard")
    
    return templates.TemplateResponse(
        request=request,
        name="login.html"
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
    user_id = Depends(verify_web_user),
    db = Depends(get_db)
    
):
    try:
        if user_id is None:
            return RedirectResponse(url="/web/login")
        dao = BackupDao(session=db)
        user_backups = await dao.get_user_backups(user_id=user_id)
        context = [BackupData(
            id=b.id,
            name=b.name_to_show,
            rows=b.rows,
            created_at=b.created_at
            ).model_dump() for b in user_backups]

        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={"backups": context}
        )
    except Exception as e:
        logger.exception(e)