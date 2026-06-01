from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from src.core.database import async_engine

from src.routers.api.passwords import api_passwords
from src.routers.api.users import api_users
from src.routers.web.passwords import web_passwords
from src.routers.web.users import web_users
from src.routers.web.static_pages import pages
from src.metrics.router import metrics
from src.metrics.middleware import logging_for_metrics

@asynccontextmanager
async def lifespan(app: FastAPI):

    yield

    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)

app.middleware("http")(logging_for_metrics)



app.mount(path="/static", app=StaticFiles(directory="static"), name="static")

# exception_response(app) 

app.include_router(api_passwords, tags=["PASSWORDS", "API"], prefix="/api")
app.include_router(api_users, tags=["USERS", "API"], prefix="/api")
app.include_router(web_passwords, tags=["PASSWORDS", "WEB"], prefix="/web")
app.include_router(web_users, tags=["USERS", "WEB"], prefix="/web")
app.include_router(pages, tags=["PAGES"])
app.include_router(metrics, tags=["METRICS"])