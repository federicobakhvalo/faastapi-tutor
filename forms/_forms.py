from forms.baseform import BaseForm
from forms.formfield import FormField, SelectField
from schemas.schemas import *


class ReaderForm(BaseForm):
    schema_class = ReaderCreateSchema

    def init_fields(self):
        self._fields = {
            "first_name": FormField("first_name", "Имя", placeholder="Имя"),
            "last_name": FormField("last_name", "Фамилия", placeholder="Фамилия"),
            "email": FormField("email", "Email", input_type="email", placeholder="example@email.com"),
            "phone": FormField("phone", "Телефон", required=False, placeholder="+7XXXXXXXXXX или 8XXXXXXXXXX"),
            "cover_url": FormField("cover_url", "Ссылка на фото (URL формат)", input_type="url", required=False,
                                   placeholder="Ссылка на аватарку читателя"),
        }


class BookForm(BaseForm):
    schema_class = BookCreateSchema

    def __init__(self, form_data=None, *, author_choices=[]):
        self.author_choices = author_choices
        super().__init__(form_data)

    def init_fields(self):
        self._fields = {
            "author_id": SelectField(
                name="author_id",
                label="Автор",
                choices=self.author_choices,
            ),
            "bookname": FormField("bookname", "Название книги", placeholder="Введите название книги"),
            "review": FormField("review", "Описание", required=False, placeholder="Описание о книге",
                                input_type="textarea", attrs={"rows": 2}),
            "amount": FormField("amount", "Количество", input_type="number", placeholder="Количество экземпляров"),
            "cover_url": FormField("cover_url", "Обложка (URL)", input_type="url",
                                   placeholder="Ссылка на обложку книги"),
        }


class BookLoanForm(BaseForm):
    schema_class = BookLoanCreateSchema

    def __init__(self, form_data=None, *, book_choices, reader_choices, librarian_choices, initial=None):
        self.book_choices = book_choices
        self.reader_choices = reader_choices
        self.librarian_choices = librarian_choices
        super().__init__(form_data, initial=initial)

    def init_fields(self):
        self._fields = {
            "book_id": SelectField("book_id", "Книга", self.book_choices),
            "reader_id": SelectField("reader_id", "Читатель", self.reader_choices),
            "librarian_id": SelectField("librarian_id", "Библиотекарь", self.librarian_choices),
            "due_date": FormField(
                "due_date",
                "Дата срока возврата книги",
                input_type="date",
            ),
        }


class BookLoanUpdateForm(BaseForm):
    schema_class = BookLoanUpdateSchema

    def init_fields(self):
        self._fields = {
            "due_date": FormField(
                "due_date",
                "Дата срока возврата книги",
                input_type="date",
            ),
            "returned_at": FormField(
                "returned_at",
                "Дата возврата книги читателем",
                input_type="date",
                required=False,
            ),
        }
