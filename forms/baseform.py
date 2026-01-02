from pydantic import ValidationError

from forms.formfield import FormField


class BaseForm:
    schema_class = None  # Pydantic схема

    def __init__(self, form_data: dict | None = None):
        self.form_data = form_data or {}
        self._fields: dict[str, FormField] = {}
        self._errors: dict[str, list[str]] = {}
        self.cleaned_data = None

        self.init_fields()
        self.bind_data()

    def init_fields(self):
        raise NotImplementedError

    def add_error(self, field: str, message: str):
        self._errors.setdefault(field, []).append(message)

    def bind_data(self):
        for name, field in self._fields.items():
            field.bind(self.form_data.get(name))

    def is_valid(self) -> bool:
        try:
            self.cleaned_data = self.schema_class(**self.form_data)
            return True
        except ValidationError as e:
            for err in e.errors():
                field = err["loc"][0]
                self._errors.setdefault(field, []).append(err["msg"])
                if field in self._fields:
                    self._fields[field].errors.append(err["msg"])
            return False

    def __iter__(self):
        return iter(self._fields.values())
