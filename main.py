from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles


from backend.core.database import async_engine, async_session
from backend.dao.role_dao import RoleDAO
from backend.dao.userDao import UserDao
from backend.core.settings import get_settings
from backend.metrics.middleware import logging_for_metrics
from backend.exceptions.handlers import auth_redirect

from backend.routers.api.passwords import api_passwords
from backend.routers.api.users import api_users
from backend.routers.api.statistic import api_statistic
from backend.routers.web.passwords import web_passwords
from backend.routers.web.users import web_users
from backend.routers.web.static_pages import pages
from backend.metrics.router import metrics

s = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session() as session:    
        roles_dao = RoleDAO(session=session)
        user_dao = UserDao(session=session)
        
        roles = await roles_dao.initialize_roles()
        await user_dao.initialize_admins()
        
        
        await session.commit()
    
    
    yield

    await async_engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    docs_url=None if s.APP_MODE == "production" else "/docs",
    redoc_url=None if s.APP_MODE == "production" else "/redoc",
    openapi_url=None if s.APP_MODE == "production" else "/openapi.json"
)

app.middleware("http")(logging_for_metrics)

auth_redirect(app=app)


app.mount(path="/static", app=StaticFiles(directory="static"), name="static")


app.include_router(api_passwords, tags=["PASSWORDS", "API"], prefix="/api")
app.include_router(api_users, tags=["USERS", "API"], prefix="/api")
app.include_router(api_statistic, tags=["STATS"], prefix="/api")
app.include_router(web_passwords, tags=["PASSWORDS", "WEB"], prefix="/web")
app.include_router(web_users, tags=["USERS", "WEB"], prefix="/web")
app.include_router(pages, tags=["PAGES"], prefix="/web")
app.include_router(metrics, tags=["METRICS"])