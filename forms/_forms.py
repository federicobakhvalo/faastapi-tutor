

from forms.baseform import BaseForm
from forms.formfield import FormField
from schemas.schemas import ReaderCreateSchema

class ReaderForm(BaseForm):
    schema_class = ReaderCreateSchema

    def init_fields(self):
        self._fields = {
            "first_name": FormField("first_name", "Имя", placeholder="Имя"),
            "last_name": FormField("last_name", "Фамилия", placeholder="Фамилия"),
            "email": FormField("email", "Email", input_type="email", placeholder="example@email.com"),
            "phone": FormField("phone", "Телефон", required=False, placeholder="+7XXXXXXXXXX или 8XXXXXXXXXX"),
            "cover_url": FormField("cover_url", "Ссылка на фото (URL формат)", input_type="url", required=False, placeholder="Ссылка на аватарку читателя"),
        }