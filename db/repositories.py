from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import DBSettings
from .api import Database
from .models import *
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from .querysets import *
from schemas.pagination import Pagination
from datetime import date, datetime, time


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


class ReaderRepository(BaseRepository):

    async def get_reader(self, reader_id: int):
        stmt = (
            ReaderQuerySet()
            .filter_by_id(reader_id)
            .with_ticket()
            .with_active_loans_count()
            .query
        )

        result = await self.session.execute(stmt)

        row = result.mappings().first()

        return dict(row) if row else None

    async def list_choices(self) -> list[tuple[int, str]]:
        result = await self.session.execute(ReaderQuerySet().list_choices().query)
        return [
            (id_, f"{first} {last}")
            for id_, first, last in result.all()
        ]

    async def create(self, data: dict) -> Reader:
        # сразу вызываем синглтон
        reader = Reader(**data)
        self.session.add(reader)
        await self.session.commit()
        await self.session.refresh(reader)
        return reader


class BookRepository(BaseRepository):

    async def exists(self, book_id: int) -> bool:

        return await self.session.get(Book, book_id) is not None

    async def list_choices(self):

        stmt = BookQueryset().select_for_choices().query
        result = await self.session.execute(stmt)
        return [
            (id_, f"{book} — {author}")
            for id_, book, author in result.all()
        ]

    async def list(self, *, page=1, page_size=10, search=None, order=None):

        qs = BookQueryset().with_author().search(search).order_by(order).query
        total = await self.session.scalar(select(func.count()).select_from(qs.subquery()))
        pagination = Pagination(page=page, page_size=page_size, total=total)

        result = await self.session.execute(
            qs.limit(page_size).offset(pagination.offset)
        )
        books = result.scalars().all()

        return books, pagination

    async def create(self, data: dict) -> Book:

        author_id = data.get('author_id', None)
        author = await self.session.get(BookAuthor, author_id)
        if not author:
            raise ValueError("Выбранный автор не существует")

        book = Book(**data)
        self.session.add(book)
        try:
            await self.session.commit()
            await self.session.refresh(book)

        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError("Не удалось создать книгу.Возможно,она существует с такими параметрами")
        return book


class LibrarianRepository(BaseRepository):

    async def list_choices(self):
        result = await self.session.execute(
            select(Librarian.id, Librarian.first_name, Librarian.last_name).order_by(Librarian.last_name))
        return [
            (id_, f"{first_name}  {last_name}")
            for id_, first_name, last_name in result.all()
        ]


class BookLoanRepository(BaseRepository):

    async def get(self, loan_id: int) -> BookLoan | None:

        return await self.session.get(BookLoan, loan_id)

    async def update(self, loan_id: int, data: dict) -> BookLoan | None:

        async with self.session.begin():
            loan = await self.session.get(BookLoan, loan_id, with_for_update=True)
            if not loan:
                raise ValueError("Выдача не найдена")
            old_returned = loan.returned_at
            new_returned = data.get('returned_at', None)
            if new_returned and new_returned <= loan.issued_at.date():
                raise ValueError("Дата возврата должна быть позже даты выдачи")
            loan.due_date = data["due_date"]
            loan.returned_at = (
                datetime.combine(new_returned, time(23, 59, 59))
                if new_returned
                else None
            )
            book = await self.session.get(Book, loan.book_id, with_for_update=True)

            if old_returned is None and new_returned is not None:
                book.amount += 1

            elif old_returned is not None and new_returned is None:
                if book.amount < 1:
                    raise ValueError(
                        "Невозможно отменить возврат — нет доступных экземпляров"
                    )
                book.amount -= 1
        await self.session.refresh(loan)
        return loan

    async def list(self, *, page=1, page_size=10, order=None):

        qs = BookLoanQueryset().as_list().order_by(order).query

        total = await self.session.scalar(select(func.count()).select_from(qs.subquery()))
        pagination = Pagination(page=page, page_size=page_size, total=total)
        result = await self.session.execute(
            qs.limit(page_size).offset(pagination.offset)
        )
        rows = result.mappings().all()
        return rows, pagination

    async def create(self, data: dict) -> BookLoan:

        try:
            async with self.session.begin():
                book = await self.session.get(Book, data['book_id'])
                if not book:
                    raise ValueError("Такой книги не существует")
                if book.amount < 1:
                    raise ValueError("такая книга недоступна для выдачи")
                book.amount -= 1

                loan = BookLoan(
                    book_id=data["book_id"],
                    reader_id=data["reader_id"],
                    librarian_id=data.get("librarian_id"),
                    due_date=data["due_date"],
                    issued_at=datetime.utcnow(),
                )
                self.session.add(loan)
            await self.session.refresh(loan)
            return loan

        except IntegrityError as E:
            raise ValueError("Эта книга уже выдана данному читателю и ещё не возвращена")


class BookAuthorRepository(BaseRepository):

    # async def list_all(self) -> list[BookAuthor]:
    #     async with db.session() as session:
    #         result = await session.execute(select(BookAuthor).order_by(BookAuthor.name))
    #         authors: list[BookAuthor] = result.scalars().all()
    #         return authors

    async def list_choices(self) -> list[tuple[int, str]]:
        result = await self.session.execute(
            select(BookAuthor.id, BookAuthor.name).order_by(BookAuthor.name)
        )
        return result.all()


class ReaderTicketRepository(BaseRepository):
    async def create(self, reader_id: int | None):

        if not reader_id:
            raise ValueError('Читатель не найден')
        ticket = ReaderTicket(reader_id=reader_id)
        self.session.add(ticket)
        try:
            await self.session.commit()
            await self.session.refresh(ticket)
        except IntegrityError as E:
            await self.session.rollback()
            raise ValueError("Возможно , у читателя уже есть билет")

        return ticket
