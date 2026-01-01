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

    def bind(self, value: str | None):
        self.value = value or ""