from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from common.validators import phone_validator
from .validators import PasswordValidator


class PhoneAuthenticationForm(forms.Form):
    phone = forms.CharField(validators=[phone_validator])


class LoginPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)


class OTPForm(forms.Form):
    code = forms.CharField(max_length=6, required=True)


class SetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password"].validators.append(PasswordValidator().validate)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error(
                "confirm_password",
                ValidationError(
                    _("تکرار رمز عبور با رمز اصلی مطابقت ندارد"),
                    code="password_mismatch",
                ),
            )
        return cleaned_data
