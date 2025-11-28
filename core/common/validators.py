import re

from django.core.exceptions import ValidationError


def phone_validator(value):
    if not re.match(r"^09\d{9}$", value):
        raise ValidationError("شماره وارد شده نامعتبر است")
