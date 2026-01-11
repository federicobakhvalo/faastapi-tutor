from contextlib import asynccontextmanager
from typing import Optional, AsyncIterator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession, AsyncEngine,
)
from sqlalchemy.orm import declarative_base
from config.db_config import DBSettings

Base = declarative_base()


# class Database:
#     _instance: Optional["Database"] = None
#     _engine = None
#     _session_factory: Optional[async_sessionmaker] = None
#
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#         return cls._instance
#
#     async def connect(self):
#
#         if self._engine is not None:
#             return
#         settings = DBSettings()
#         self._engine = create_async_engine(
#             settings.url,
#             echo=True,  # выключить на проде
#             pool_pre_ping=True,
#         )
#
#         self._session_factory = async_sessionmaker(
#             self._engine,
#             expire_on_commit=False,
#         )
#
#     async def close(self):
#         if self._engine:
#             await self._engine.dispose()
#             self._engine = None
#             self._session_factory = None
#
#     def session(self) -> AsyncSession:
#         if not self._session_factory:
#             raise RuntimeError("Database not connected")
#         return self._session_factory()
#

class Database:
    def __init__(
            self,
            url: str,
            *,
            pool_size: int = 10,
            max_overflow: int = 20,
            pool_timeout: int = 30,
            echo: bool = False,
    ) -> None:
        self._url: str = url
        self._pool_size: int = pool_size
        self._max_overflow: int = max_overflow
        self._pool_timeout: int = pool_timeout
        self._echo: bool = echo

        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[
            async_sessionmaker[AsyncSession]
        ] = None

    async def connect(self) -> None:
        if self._engine is not None:
            return

        self._engine = create_async_engine(
            self._url,
            echo=self._echo,
            pool_pre_ping=True,
            pool_size=self._pool_size,
            max_overflow=self._max_overflow,
            pool_timeout=self._pool_timeout,
        )

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )

    async def close(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    def get_session(self) -> AsyncSession:
        if not self._session_factory:
            raise RuntimeError("Database not connected")
        return self._session_factory()

    # @asynccontextmanager
    # async def get_session(self) -> AsyncIterator[AsyncSession]:
    #     if not self._session_factory:
    #         raise RuntimeError("Database not connected")
    #
    #     session = self._session_factory()
    #     try:
    #         yield session
    #     finally:
    #         await session.close()
