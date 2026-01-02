from forms.baseform import BaseForm
from forms.formfield import FormField, SelectField
from schemas.schemas import ReaderCreateSchema, BookCreateSchema


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

    def __init__(self, form_data=None, *, author_choices):
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
            "review": FormField("review", "Описание", required=False, placeholder="Ваш отзыв по книге"),
            "amount": FormField("amount", "Количество", input_type="number"),
            "cover_url": FormField("cover_url", "Обложка (URL)", input_type="url",
                                   placeholder="Ссылка на обложку книги"),
        }
