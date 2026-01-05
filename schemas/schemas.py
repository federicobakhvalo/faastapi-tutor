from pydantic import BaseModel, EmailStr, HttpUrl, field_validator, Field
from typing import Optional
from datetime import date
import re


class ReaderCreateSchema(BaseModel):
    first_name: str = Field(..., min_length=1, description="Имя должно быть хотя бы 1 символ")
    last_name: str = Field(..., min_length=1, description="Фамилия должна быть хотя бы 1 символ")
    email: EmailStr
    phone: Optional[str] = Field(
        None,
        pattern=r'^(\+7|8)\d{10}$',
        description="Телефон должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX"
    )
    cover_url: Optional[HttpUrl] = None

    @field_validator("phone", "cover_url", mode='before')
    @classmethod
    def empty_to_none(cls, v):
        if v is None:
            return None
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator("first_name", "last_name", mode='before')
    @classmethod
    def strip_names(cls, v: str) -> str:
        return v.strip()


class BookCreateSchema(BaseModel):
    author_id: int
    bookname: str = Field(..., min_length=1)
    review: str | None = None
    amount: int = Field(ge=0)
    cover_url: HttpUrl

    @field_validator("bookname", "review", mode="before")
    @classmethod
    def strip(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("review", mode="before")
    @classmethod
    def empty_to_none(cls, v):
        if v == "":
            return None
        return v

    @field_validator("cover_url")
    @classmethod
    def validate_image_extension(cls, v: HttpUrl) -> HttpUrl:
        allowed_ext = (".jpg", ".jpeg", ".png", ".webp")
        url = str(v).lower()
        if not url.endswith(allowed_ext):
            raise ValueError(
                "URL обложки должен оканчиваться на .jpg, .jpeg, .png или .webp"
            )
        return v


class BookLoanCreateSchema(BaseModel):
    book_id: int
    reader_id: int
    librarian_id: int
    due_date: date

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: date):
        if v <= date.today():
            raise ValueError("Дата возврата должна быть в будущем")
        return v


class BookLoanUpdateSchema(BaseModel):
    due_date: date
    returned_at: date | None = None

    @field_validator("returned_at", mode="before")
    @classmethod
    def empty_to_none(cls, v):
        if v == "":
            return None
        return v
