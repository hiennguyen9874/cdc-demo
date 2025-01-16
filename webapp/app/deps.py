from typing import AsyncIterator

from elasticsearch import AsyncElasticsearch
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_connection import async_db_connection
from app.core.es_connection import async_es_connection


async def get_async_db() -> AsyncIterator[AsyncSession]:
    async with async_db_connection.session() as db:
        yield db


async def get_async_es() -> AsyncIterator[AsyncElasticsearch]:
    async with async_es_connection.session() as es:
        yield es
