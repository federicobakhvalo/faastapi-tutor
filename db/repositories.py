from api import Database
from models import *

db = Database()


class ReaderRepository:
    async def create(self, data: dict) -> Reader:
        async with db.session() as session:  # сразу вызываем синглтон
            reader = Reader(**data)
            session.add(reader)
            await session.commit()
            await session.refresh(reader)
            return reader
