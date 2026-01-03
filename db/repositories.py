from .api import Database
from .models import *
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

db = Database()


class ReaderRepository:
    async def create(self, data: dict) -> Reader:
        async with db.session() as session:  # сразу вызываем синглтон
            reader = Reader(**data)
            session.add(reader)
            await session.commit()
            await session.refresh(reader)
            return reader


class BookRepository:
    async def create(self, data: dict) -> Book:
        async with db.session() as session:
            author_id = data.get('author_id', None)
            author = await session.get(BookAuthor, author_id)
            if not author:
                raise ValueError("Выбранный автор не существует")

            book = Book(**data)
            session.add(book)
            try:
                await session.commit()
                await session.refresh(book)

            except IntegrityError as e:
                await session.rollback()
                raise ValueError("Не удалось создать книгу.Возможно,она существует с такими параметрами")
            return book


class BookAuthorRepository:

    # async def list_all(self) -> list[BookAuthor]:
    #     async with db.session() as session:
    #         result = await session.execute(select(BookAuthor).order_by(BookAuthor.name))
    #         authors: list[BookAuthor] = result.scalars().all()
    #         return authors

    async def list_choices(self) -> list[tuple[int, str]]:
        async with Database().session() as session:
            result = await session.execute(
                select(BookAuthor.id, BookAuthor.name).order_by(BookAuthor.name)
            )
            return result.all()
