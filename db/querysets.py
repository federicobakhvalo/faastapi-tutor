from sqlalchemy import select, or_
from sqlalchemy.orm import contains_eager

from .models import *


class BookQueryset:
    def __init__(self):
        self._stmt = select(Book)
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

    def order_by(self, field: str | None):
        if field:
            desc = field.startswith('-')
            field_name = field.lstrip('-')
            column = getattr(Book, field_name, None)
            if column:
                self._stmt = self._stmt.order_by(column.desc() if desc else column.asc())

        else:
            self._stmt = self._stmt.order_by(Book.id)

        return self

    @property
    def query(self):
        return self._stmt
