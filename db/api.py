from typing import Optional
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import declarative_base
from config.db_config import DBSettings

Base = declarative_base()


class Database:
    _instance: Optional["Database"] = None
    _engine = None
    _session_factory: Optional[async_sessionmaker] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self):
        if self._engine is not None:
            return

        settings = DBSettings()

        print(settings.url)

        self._engine = create_async_engine(
            settings.url,
            echo=True,               # выключить на проде
            pool_pre_ping=True,
        )

        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
        )

    async def close(self):
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    def session(self) -> AsyncSession:
        if not self._session_factory:
            raise RuntimeError("Database not connected")
        return self._session_factory()

