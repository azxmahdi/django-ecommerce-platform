from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from account.validators import PasswordValidator
from common.validators import phone_validator


User = get_user_model()


class PasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(
        widget=forms.PasswordInput, validators=[PasswordValidator().validate]
    )
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if (
            new_password
            and confirm_password
            and new_password != confirm_password
        ):
            raise ValidationError(
                _("رمز عبور جدید و تأییدیه آن مطابقت ندارند."),
                code="password_mismatch",
            )

        return cleaned_data


class FirstnameAndLastnameForm(forms.Form):
    first_name = forms.CharField(max_length=225, required=True)
    last_name = forms.CharField(max_length=225, required=True)


class PhoneForm(forms.Form):
    phone = forms.CharField(validators=[phone_validator])

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("این شماره قبلاً ثبت شده است.")
        return phone
