from sqlalchemy import select, or_, func
from sqlalchemy.orm import contains_eager

from .models import *


class BaseQuerySet:
    def __init__(self, model_class):
        self.model_class = model_class
        self._stmt = select(model_class)

    def filter_by_id(self, obj_id: int):
        self._stmt = self._stmt.where(self.model_class.id == obj_id)
        return self

    def one(self):
        self._stmt = self._stmt.limit(1)
        return self

    def order_by(self, field: str | None):
        if field:
            desc = field.startswith('-')
            field_name = field.lstrip('-')
            column = getattr(self.model_class, field_name, None)
            if column:
                self._stmt = self._stmt.order_by(column.desc() if desc else column.asc())

        else:
            self._stmt = self._stmt.order_by(self.model_class.id)

        return self

    @property
    def query(self):
        return self._stmt


class ReaderQuerySet(BaseQuerySet):
    def __init__(self):
        super().__init__(Reader)
        self._joined_ticket = False

    def list_choices(self):
        self._stmt = (
            select(
                Reader.id,
                Reader.first_name,
                Reader.last_name,
            )
            .order_by(Reader.last_name, Reader.first_name)
        )
        return self

    def with_ticket(self):
        if not self._joined_ticket:
            self._stmt = (
                self._stmt
                .outerjoin(ReaderTicket, ReaderTicket.reader_id == Reader.id)
                .add_columns(
                    ReaderTicket.code.label("ticket_code"),
                    ReaderTicket.is_active.label("ticket_active"),
                )
            )
            self._joined_ticket = True
        return self

    def with_active_loans_count(self):
        subq = (
            select(
                BookLoan.reader_id,
                func.count(BookLoan.id).label("active_loans"),
            )
            .where(BookLoan.returned_at.is_(None))
            .group_by(BookLoan.reader_id)
            .subquery()
        )

        self._stmt = (
            self._stmt
            .outerjoin(subq, subq.c.reader_id == Reader.id)
            .add_columns(
                func.coalesce(subq.c.active_loans, 0).label("active_loans")
            )
        )
        return self


class BookQueryset(BaseQuerySet):
    def __init__(self):
        super().__init__(Book)
        self._joined_author = False

    def select_for_choices(self):
        self._stmt = (
            select(
                Book.id,
                Book.bookname,
                BookAuthor.name,
            )
            .join(Book.author)
        )
        return self

    def with_author(self):
        if not self._joined_author:
            self._stmt = (
                self._stmt
                .join(Book.author)
                .options(contains_eager(Book.author))
            )
            self._joined_author = True
        return self

    def search(self, text: str | None):
        if text:
            self.with_author()
            pattern = f'%{text}%'
            self._stmt = self._stmt.where(or_(Book.bookname.ilike(pattern), BookAuthor.name.ilike(pattern)))

        return self


class BookLoanQueryset(BaseQuerySet):
    def __init__(self):
        super().__init__(BookLoan)

    def as_list(self):
        self._stmt = (
            select(
                BookLoan.id,
                BookLoan.issued_at,
                BookLoan.returned_at,
                Book.bookname.label("bookname"),
                func.concat_ws(" ", Reader.first_name, Reader.last_name).label("reader_name"),
                func.concat_ws(" ", Librarian.first_name, Librarian.last_name).label("librarian_name"),
            )
            .join(Book)
            .join(Reader)
            .outerjoin(Librarian)
        )
        return self
