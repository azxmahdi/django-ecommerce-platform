import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PasswordValidator:

    def validate(self, password):
        errors = []

        if len(password) < 8:
            errors.append("حداقل ۸ کاراکتر لازم است.")
        if not re.search(r"[A-Z]", password):
            errors.append("حداقل یک حرف بزرگ انگلیسی نیاز است.")
        if not re.search(r"[a-z]", password):
            errors.append("حداقل یک حرف کوچک انگلیسی نیاز است.")
        if not re.search(r"[0-9]", password):
            errors.append("حداقل یک عدد نیاز است.")
        if not any(
            char in ["@", "#", "$", "%", "^", "&", "*", "/"]
            for char in password
        ):
            errors.append("حداقل یک نماد خاص نیاز است.")

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            "رمز عبور باید حداقل ۸ کاراکتر و شامل ح"
            "روف بزرگ، کوچک، عدد و نماد باشد."
        )
