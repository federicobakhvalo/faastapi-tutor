import uuid

from sqlalchemy.orm import DeclarativeBase

from typing import Optional, List
from datetime import datetime
from sqlalchemy import (
    BigInteger,
    String,
    DateTime, Boolean,

)
from sqlalchemy import String, Text, Integer, ForeignKey, UniqueConstraint, Date, Index

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class BookAuthor(Base):
    __tablename__ = "library_app_bookauthor"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    books: Mapped[List["Book"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return self.name


class Book(Base):
    __tablename__ = "library_app_book"

    id: Mapped[int] = mapped_column(primary_key=True)

    author_id: Mapped[int] = mapped_column(
        ForeignKey("library_app_bookauthor.id", ondelete="CASCADE"),
        nullable=False
    )

    bookname: Mapped[str] = mapped_column(String(100), nullable=False)
    review: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    amount: Mapped[int] = mapped_column(Integer, default=0)
    cover_url: Mapped[str] = mapped_column(String(1000), nullable=False)

    author: Mapped["BookAuthor"] = relationship(back_populates="books")
    loans: Mapped[List["BookLoan"]] = relationship(back_populates="book")

    __table_args__ = (
        UniqueConstraint(
            "author_id",
            "bookname",
            name="unique_book_per_author"
        ),
    )

    def __repr__(self) -> str:
        return f"{self.bookname} - {self.author}"


class Reader(Base):
    __tablename__ = "library_app_reader"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
        unique=True
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    cover_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True
    )

    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )

    # relations (НЕ создают таблицы, только ORM)
    loans: Mapped[List["BookLoan"]] = relationship(
        back_populates="reader"
    )

    ticket: Mapped[Optional["ReaderTicket"]] = relationship(
        back_populates="reader",
        uselist=False
    )

    def __repr__(self) -> str:
        return f"<Reader {self.first_name} {self.last_name}>"


class Librarian(Base):
    __tablename__ = "library_app_librarian"

    id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    cover_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    hired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    issued_loans: Mapped[List["BookLoan"]] = relationship(back_populates="librarian")

    def __repr__(self) -> str:
        return f"{self.first_name} - {self.last_name}"


class BookLoan(Base):
    __tablename__ = "library_app_bookloan"

    id: Mapped[int] = mapped_column(primary_key=True)

    reader_id: Mapped[int] = mapped_column(
        ForeignKey("library_app_reader.id", ondelete="CASCADE"),
        nullable=False
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("library_app_book.id", ondelete="CASCADE"),
        nullable=False
    )
    librarian_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("library_app_librarian.id", ondelete="SET NULL"),
        nullable=True
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    due_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    returned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    reader: Mapped["Reader"] = relationship(back_populates="loans")
    book: Mapped["Book"] = relationship(back_populates="loans")
    librarian: Mapped[Optional["Librarian"]] = relationship(back_populates="issued_loans")

    __table_args__ = (
        Index(
            "unique_active_bookloan",
            "book_id",
            "reader_id",
            unique=True,
            postgresql_where=(returned_at.is_(None)),
        ),
    )

    def __repr__(self) -> str:
        return f"{self.book} → {self.reader}"


class ReaderTicket(Base):
    __tablename__ = "library_app_readerticket"

    id: Mapped[int] = mapped_column(primary_key=True)

    reader_id: Mapped[int] = mapped_column(
        ForeignKey("library_app_reader.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    reader: Mapped["Reader"] = relationship(back_populates="ticket")

    def __init__(self, **kwargs):
        if "code" not in kwargs:
            kwargs["code"] = uuid.uuid4().hex[:12].upper()
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"Билет {self.code} — {self.reader}"
