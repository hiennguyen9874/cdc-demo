from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.custom_logging import make_customize_logger
from app.core.db_connection import async_db_connection
from app.core.es_connection import async_es_connection
from app.core.settings import settings
from app.routers.item import router as item_router

make_customize_logger(settings.APP.CONFIG_DIR / "logging.json")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    logger.info("FastAPI startup...")
    async_db_connection.init()
    async_es_connection.init()

    yield

    await async_db_connection.close()
    await async_es_connection.close()

    logger.info("FastAPI shutdown...")


app = FastAPI(
    redirect_slashes=True,
    lifespan=lifespan,
)

app.add_middleware(  # type: ignore
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(item_router, prefix="/item")
