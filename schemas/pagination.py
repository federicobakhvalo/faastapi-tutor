from pydantic import BaseModel


class Pagination(BaseModel):
    page: int
    page_size: int
    total: int

    @property
    def is_paginated(self):
        return self.has_prev or self.has_next

    @property
    def offset(self):
        return (self.page - 1) * self.page_size

    @property
    def pages(self):
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages
