from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاریخ ایجاد")
    )
    updated_date = models.DateTimeField(
        auto_now=True, verbose_name=_("تاریخ به‌روزرسانی")
    )

    class Meta:
        abstract = True
        ordering = ("-created_date",)


class SupportInfoModel(TimeStampedModel):
    phone = models.CharField(max_length=20, verbose_name=_("تلفن"))
    email = models.EmailField(verbose_name=_("ایمیل"))
    headquarters_address = models.TextField(verbose_name=_("آدرس دفتر مرکزی"))

    class Meta:
        verbose_name = _("اطلاعات پشتیبانی")
        verbose_name_plural = _("اطلاعات پشتیبانی")

    def __str__(self):
        return f"پشتیبانی ({self.phone})"
