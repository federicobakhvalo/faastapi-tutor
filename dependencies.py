from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_entry import db


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with db.get_session() as session:
        yield session
