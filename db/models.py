from sqlalchemy.orm import DeclarativeBase

from typing import Optional, List
from datetime import datetime
from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


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
