from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.database import async_engine

from src.exceptions.handlers import exception_response

from src.api.passwords import passwords as pass_router
from src.api.users import users as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield

    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)

exception_response(app)

app.include_router(pass_router, tags=["PASSWORDS"])
app.include_router(users_router, tags=["USERS"])
