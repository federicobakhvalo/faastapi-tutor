from pydantic import BaseModel, EmailStr, HttpUrl, field_validator,Field
from typing import Optional
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

    @field_validator("phone", "cover_url",mode='before')
    @classmethod
    def empty_to_none(cls, v):
        # Если пустая строка — превращаем в None
        if v is None:
            return None
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator("first_name", "last_name",mode='before')
    @classmethod
    def strip_names(cls, v: str) -> str:
        """Удаляем пробелы в начале и конце"""
        return v.strip()