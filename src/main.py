from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from src.core.database import async_engine


from src.api.passwords import passwords as pass_router
from src.api.users import users as users_router
from src.api.static_pages import pages
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

app.include_router(pass_router, tags=["PASSWORDS"])
app.include_router(users_router, tags=["USERS"])
app.include_router(pages, tags=["PAGES"])
app.include_router(metrics, tags=["METRICS"])