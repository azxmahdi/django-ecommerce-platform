from django.db import models
from django.utils.translation import gettext_lazy as _

from common.validators import phone_validator
from common.models import TimeStampedModel


class ContactModel(TimeStampedModel):
    name = models.CharField(max_length=400, verbose_name=_("نام"))
    phone = models.CharField(
        max_length=11, validators=[phone_validator], verbose_name=_("تلفن")
    )
    email = models.EmailField(
        error_messages={"invalid": _("ایمیل وارد شده نا معتبر است")},
        verbose_name=_("ایمیل"),
    )
    message = models.TextField(verbose_name=_("پیام"))

    class Meta:
        verbose_name = _("تماس")
        verbose_name_plural = _("تماس‌ها")

    def __str__(self):
        return self.name
