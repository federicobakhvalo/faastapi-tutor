from .api import Database
from .models import *
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from .querysets import *
from schemas.pagination import Pagination

db = Database()


class ReaderRepository:

    async def list_choices(self) -> list[tuple[int, str]]:
        async with db.session() as session:
            result = await session.execute(
                select(
                    Reader.id,
                    Reader.first_name,
                    Reader.last_name,
                ).order_by(Reader.last_name, Reader.first_name)
            )
            return [
                (id_, f"{first} {last}")
                for id_, first, last in result.all()
            ]

    async def create(self, data: dict) -> Reader:
        async with db.session() as session:  # сразу вызываем синглтон
            reader = Reader(**data)
            session.add(reader)
            await session.commit()
            await session.refresh(reader)
            return reader


class BookRepository:

    async def list_choices(self):
        async with db.session() as session:
            stmt = BookQueryset().select_for_choices().query
            result = await session.execute(stmt)
            return [
                (id_, f"{book} — {author}")
                for id_, book, author in result.all()
            ]

    async def list(self, *, page=1, page_size=10, search=None, order=None):

        async with db.session() as session:
            qs = BookQueryset().with_author().search(search).order_by(order).query
            total = await session.scalar(select(func.count()).select_from(qs.subquery()))
            pagination = Pagination(page=page, page_size=page_size, total=total)

            result = await session.execute(
                qs.limit(page_size).offset(pagination.offset)
            )
            books = result.scalars().all()

        return books, pagination

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
