from .api import Database
from .models import *
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from .querysets import *
from schemas.pagination import Pagination
from datetime import date, datetime, time

db = Database()


class ReaderRepository:

    async def get_reader(self, reader_id: int):
        async with db.session() as session:
            stmt = (
                ReaderQuerySet()
                .filter_by_id(reader_id)
                .with_ticket()
                .with_active_loans_count()
                .query
            )

            result = await session.execute(stmt)
            row = result.mappings().first()

            return dict(row) if row else None

    async def list_choices(self) -> list[tuple[int, str]]:
        async with db.session() as session:
            result = await session.execute(ReaderQuerySet().list_choices().query)
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

    async def exists(self, book_id: int) -> bool:
        async with db.session() as session:
            return await session.get(Book, book_id) is not None

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


class LibrarianRepository:

    async def list_choices(self):
        async with db.session() as session:
            result = await session.execute(
                select(Librarian.id, Librarian.first_name, Librarian.last_name).order_by(Librarian.last_name))
            return [
                (id_, f"{first_name}  {last_name}")
                for id_, first_name, last_name in result.all()
            ]


class BookLoanRepository:

    async def get(self, loan_id: int) -> BookLoan | None:
        async with db.session() as session:
            return await session.get(BookLoan, loan_id)

    async def update(self, loan_id: int, data: dict) -> BookLoan | None:
        async with db.session() as session:
            async with session.begin():
                loan = await session.get(BookLoan, loan_id, with_for_update=True)
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
                book = await session.get(Book, loan.book_id, with_for_update=True)

                if old_returned is None and new_returned is not None:
                    book.amount += 1

                elif old_returned is not None and new_returned is None:
                    if book.amount < 1:
                        raise ValueError(
                            "Невозможно отменить возврат — нет доступных экземпляров"
                        )
                    book.amount -= 1
            await session.refresh(loan)
            return loan

    async def list(self, *, page=1, page_size=10, order=None):
        async with db.session() as session:
            qs = BookLoanQueryset().as_list().order_(order).query

            total = await session.scalar(select(func.count()).select_from(qs.subquery()))
            pagination = Pagination(page=page, page_size=page_size, total=total)
            result = await session.execute(
                qs.limit(page_size).offset(pagination.offset)
            )
            rows = result.mappings().all()
            return rows, pagination

    async def create(self, data: dict) -> BookLoan:
        async with db.session() as session:
            try:
                async with session.begin():
                    book = await session.get(Book, data['book_id'])
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
                    session.add(loan)
                await session.refresh(loan)
                return loan

            except IntegrityError as E:
                raise ValueError("Эта книга уже выдана данному читателю и ещё не возвращена")


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


class ReaderTicketRepository:
    async def create(self, reader_id: int | None):
        async with db.session() as session:
            if not reader_id:
                raise ValueError('Читатель не найден')
            ticket = ReaderTicket(reader_id=reader_id)
            session.add(ticket)
            try:
                await session.commit()
                await session.refresh(ticket)
            except IntegrityError as E:
                await session.rollback()
                raise ValueError("Возможно , у читателя уже есть билет")

            return ticket
