from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import TimeStampedModel


class SiteInfoModel(TimeStampedModel):
    store_name = models.CharField(
        max_length=255, verbose_name=_("نام فروشگاه")
    )
    logo = models.ImageField(upload_to="site/logo/", verbose_name=_("لوگو"))
    support_email = models.EmailField(
        max_length=255, verbose_name=_("ایمیل پشتیبانی")
    )
    support_phone = models.CharField(
        max_length=20, verbose_name=_("تلفن پشتیبانی")
    )
    head_office_address = models.TextField(verbose_name=_("آدرس دفتر مرکزی"))
    support_hours = models.CharField(
        max_length=100, verbose_name=_("ساعات کاری پشتیبانی")
    )

    class Meta:
        verbose_name = _("اطلاعات سایت")
        verbose_name_plural = _("اطلاعات سایت")

    def __str__(self):
        return self.store_name


class SiteResourceType(models.IntegerChoices):
    SOCIAL = 1, _("شبکه اجتماعی")
    LICENSE = 2, _("مجوز سایت")


class SiteResourceModel(TimeStampedModel):
    type = models.IntegerField(
        choices=SiteResourceType.choices, verbose_name=_("نوع")
    )
    url = models.URLField(verbose_name=_("آدرس"))
    logo = models.ImageField(
        upload_to="site/resources/", verbose_name=_("لوگو")
    )

    def get_type(self):
        return {
            "id": self.type,
            "title": SiteResourceType(self.type).name,
            "label": SiteResourceType(self.type).label,
        }

    class Meta:
        verbose_name = _("منبع سایت")
        verbose_name_plural = _("منابع سایت")

    def __str__(self):
        return f"{self.get_type_display()} - {self.url}"
