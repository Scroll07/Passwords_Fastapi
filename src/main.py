from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.database import async_engine



@asynccontextmanager
async def lifespan(app: FastAPI):

    yield
    
    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)







