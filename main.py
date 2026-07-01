from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles


from src.core.database import async_engine, async_session
from src.dao.role_dao import RoleDAO
from src.dao.userDao import UserDao
from src.core.settings import get_settings
from src.metrics.middleware import logging_for_metrics

from src.routers.api.passwords import api_passwords
from src.routers.api.users import api_users
from src.routers.api.statistic import api_statistic
from src.routers.web.passwords import web_passwords
from src.routers.web.users import web_users
from src.routers.web.static_pages import pages
from src.metrics.router import metrics

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



app.mount(path="/static", app=StaticFiles(directory="static"), name="static")


app.include_router(api_passwords, tags=["PASSWORDS", "API"], prefix="/api")
app.include_router(api_users, tags=["USERS", "API"], prefix="/api")
app.include_router(api_statistic, tags=["STATS"], prefix="/api")
app.include_router(web_passwords, tags=["PASSWORDS", "WEB"], prefix="/web")
app.include_router(web_users, tags=["USERS", "WEB"], prefix="/web")
app.include_router(pages, tags=["PAGES"])
app.include_router(metrics, tags=["METRICS"])