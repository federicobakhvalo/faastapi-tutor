from pydantic import BaseModel, EmailStr, HttpUrl, field_validator
from typing import Optional
import re

class ReaderCreateSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    cover_url: Optional[HttpUrl] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]):
        if not v:
            return v
        phone_regex = r'^(\+7|8)\d{10}$'
        if not re.match(phone_regex, v):
            raise ValueError(
                'Телефон должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX'
            )
        return v