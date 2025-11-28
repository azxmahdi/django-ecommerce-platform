from datetime import timedelta

from django.db import models
from django.db.models import JSONField
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from common.models import TimeStampedModel


User = get_user_model()


class PaymentGatewayType(models.TextChoices):
    ZARINPAL = "zarinpal", _("زرین‌پال")


class PaymentStatusType(models.IntegerChoices):
    PENDING = 1, _("در انتظار")
    SUCCESS = 2, _("پرداخت موفق")
    FAILED = 3, _("پرداخت ناموفق")


class PaymentGateway(models.Model):
    name = models.CharField(
        max_length=50,
        choices=PaymentGatewayType.choices,
        verbose_name=_("نام"),
    )
    display_name = models.CharField(
        max_length=100, verbose_name=_("نام نمایشی")
    )
    image = models.ImageField(
        upload_to="payment_gateways/", verbose_name=_("تصویر")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("ترتیب"))

    config = JSONField(default=dict, blank=True, verbose_name=_("پیکربندی"))

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("درگاه پرداخت")
        verbose_name_plural = _("درگاه‌های پرداخت")

    def __str__(self):
        return self.display_name


class PaymentModel(TimeStampedModel):
    gateway = models.ForeignKey(
        PaymentGateway,
        on_delete=models.PROTECT,
        related_name="payment",
        verbose_name=_("درگاه پرداخت"),
    )
    order = models.ForeignKey(
        "order.OrderModel",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="payment",
        verbose_name=_("سفارش"),
    )
    authority_id = models.CharField(
        max_length=255, verbose_name=_("شناسه مجوز")
    )
    ref_id = models.BigIntegerField(
        null=True, blank=True, verbose_name=_("شناسه مرجع")
    )
    amount = models.DecimalField(
        default=0, max_digits=10, decimal_places=0, verbose_name=_("مبلغ")
    )
    response_json = JSONField(default=dict, verbose_name=_("پاسخ JSON"))
    response_code = models.IntegerField(
        null=True, blank=True, verbose_name=_("کد پاسخ")
    )
    status = models.IntegerField(
        choices=PaymentStatusType.choices,
        default=PaymentStatusType.PENDING,
        verbose_name=_("وضعیت"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("کاربر"),
    )

    description = models.TextField(blank=True, verbose_name=_("توضیحات"))

    class Meta:
        verbose_name = _("پرداخت")
        verbose_name_plural = _("پرداخت‌ها")

    def __str__(self):
        return f"{self.authority_id} - {self.gateway.display_name}"

    @property
    def expired_date(self):
        return self.created_date + timedelta(minutes=11)
