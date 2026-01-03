class FormField:
    def __init__(
            self,
            name: str,
            label: str,
            input_type: str = "text",
            required: bool = True,
            placeholder: str | None = None,
            attrs: dict | None = None,
            extra_class: str = "",
    ):
        self.name = name
        self.label = label
        self.input_type = input_type
        self.required = required
        self.placeholder = placeholder or ""
        self.attrs = attrs or {}
        self.extra_class = extra_class
        self.value: str = ""
        self.errors: list[str] = []

    def bind(self, value):
        self.value = "" if value is None else str(value)


class SelectField(FormField):
    def __init__(
            self,
            name: str,
            label: str,
            choices: list[tuple],
            required: bool = True,
            placeholder: str | None = None,
            attrs: dict | None = None,
            extra_class: str = ""
    ):
        super().__init__(name, label, required=required, input_type="select", placeholder=placeholder, attrs=attrs,
                         extra_class=extra_class)
        self.choices = choices
