from contextlib import asynccontextmanager, contextmanager
from functools import wraps
from typing import AsyncGenerator, Awaitable, Callable, Iterator, ParamSpec, TypeVar

from elasticsearch import AsyncElasticsearch, Elasticsearch
from loguru import logger

from app.core.settings import settings

Param = ParamSpec("Param")
RetType = TypeVar("RetType")


class AsyncESConnection:
    def __init__(self) -> None:
        self.es: AsyncElasticsearch | None = None

    def init(
        self,
        timeout: int = settings.ES.TIMEOUT,
        max_retries: int = settings.ES.MAX_RETRIES,
        retry_on_timeout: bool = settings.ES.RETRY_ON_TIMEOUT,
        connections_per_node: int = settings.ES.CONNECTIONS_PER_NODE,
    ) -> None:
        self.es = AsyncElasticsearch(
            settings.ES.URL,
            timeout=timeout,
            max_retries=max_retries,
            retry_on_timeout=retry_on_timeout,
            connections_per_node=connections_per_node,
        )

    async def close(self) -> None:
        if self.es is None:
            logger.warning("can't close connection not init")
            return

        await self.es.close()
        self.es = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncElasticsearch, None]:
        assert self.es is not None, "must call async_es_connection.init() before"
        yield self.es

    def inject(
        self,
        func: Callable[Param, Awaitable[RetType]],
    ) -> Callable[..., Awaitable[RetType]]:
        @wraps(func)
        async def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
            async with self.session() as es:
                kwargs["es"] = es
                return await func(*args, **kwargs)

        return wrapper


class SyncESConnection:
    def __init__(self) -> None:
        self.es: Elasticsearch | None = None

    def init(
        self,
        timeout: int = settings.ES.TIMEOUT,
        max_retries: int = settings.ES.MAX_RETRIES,
        retry_on_timeout: bool = settings.ES.RETRY_ON_TIMEOUT,
        connections_per_node: int = settings.ES.CONNECTIONS_PER_NODE,
    ) -> None:
        self.es = Elasticsearch(
            settings.ES.URL,
            timeout=timeout,
            max_retries=max_retries,
            retry_on_timeout=retry_on_timeout,
            connections_per_node=connections_per_node,
        )

    def close(self) -> None:
        if self.es is None:
            logger.warning("can't close connection not init")
            return

        self.es.close()
        self.es = None

    @contextmanager
    def session(self) -> Iterator[Elasticsearch]:
        assert self.es is not None, "must call sync_es_connection.init() before"

        yield self.es

    def inject(
        self,
        func: Callable[Param, RetType],
    ) -> Callable[..., RetType]:
        @wraps(func)
        def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
            with self.session() as es:
                kwargs["es"] = es
                return func(*args, **kwargs)

        return wrapper


async_es_connection = AsyncESConnection()
sync_es_connection = SyncESConnection()
