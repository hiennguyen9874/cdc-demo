from contextlib import asynccontextmanager, contextmanager
from functools import wraps
from typing import AsyncGenerator, Awaitable, Callable, Iterator, ParamSpec, TypeVar

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import settings

Param = ParamSpec("Param")
RetType = TypeVar("RetType")


class AsyncDbConnection:
    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.session_maker: async_sessionmaker[AsyncSession] | None = None

    def init(
        self,
        pool_size: int = settings.SQLALCHEMY.POOL_SIZE,
        max_overflow: int = settings.SQLALCHEMY.MAX_OVERFLOW,
        pool_timeout: int = settings.SQLALCHEMY.POOL_TIMEOUT,
    ) -> None:
        self.engine = create_async_engine(
            settings.DB.ASYNC_DATABASE_URI,
            echo=settings.SQLALCHEMY.ECHO,
            pool_pre_ping=True,
            future=True,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
        )
        self.session_maker = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def close(self) -> None:
        if self.engine is None:
            logger.warning("can't close connection not init")
            return

        await self.engine.dispose()
        self.engine = None
        self.session_marker = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        assert self.session_maker is not None, "must call async_db_connection.init() before"

        async with self.session_maker() as session:
            yield session

    def inject(
        self,
        func: Callable[Param, Awaitable[RetType]],
    ) -> Callable[..., Awaitable[RetType]]:
        @wraps(func)
        async def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
            async with self.session() as db:
                kwargs["db"] = db
                return await func(*args, **kwargs)

        return wrapper


class SyncDbConnection:
    def __init__(self) -> None:
        self.engine: Engine | None = None
        self.session_maker: sessionmaker[Session] | None = None

    def init(
        self,
        pool_size: int = settings.SQLALCHEMY.POOL_SIZE,
        max_overflow: int = settings.SQLALCHEMY.MAX_OVERFLOW,
        pool_timeout: int = settings.SQLALCHEMY.POOL_TIMEOUT,
    ) -> None:
        self.engine = create_engine(
            str(settings.DB.DATABASE_URI),
            echo=settings.SQLALCHEMY.ECHO,
            pool_pre_ping=True,
            future=True,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
        )
        self.session_maker = sessionmaker(
            self.engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )  # type: ignore

    def close(self) -> None:
        if self.engine is None:
            logger.warning("can't close connection not init")
            return

        self.engine.dispose()
        self.engine = None
        self.session_marker = None

    @contextmanager
    def session(self) -> Iterator[Session]:
        assert self.session_maker is not None, "must call sync_db_connection.init() before"

        with self.session_maker() as session:
            yield session

    def inject(
        self,
        func: Callable[Param, RetType],
    ) -> Callable[..., RetType]:
        @wraps(func)
        def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
            with self.session() as db:
                kwargs["db"] = db
                return func(*args, **kwargs)

        return wrapper


async_db_connection = AsyncDbConnection()
sync_db_connection = SyncDbConnection()
