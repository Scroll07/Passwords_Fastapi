from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from src.main import templates
from src.core.logger import get_logger

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
    
@pages.get(path="/product", response_class=HTMLResponse)
async def product(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="product.html"
    )

@pages.get(path="/how_it_works", response_class=HTMLResponse)
async def how_it_works(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="how_it_works.html"
    )

@pages.get(path="/pricing", response_class=HTMLResponse)
async def pricing(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pricing.html"
    )

@pages.get(path="/faq", response_class=HTMLResponse)
async def faq(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="faq.html"
    )

@pages.get(path="/docs", response_class=HTMLResponse)
async def docs(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="docs.html"
    )
