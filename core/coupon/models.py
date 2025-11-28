from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.models import TimeStampedModel

User = get_user_model()


class CouponModel(TimeStampedModel):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name=_("کاربر")
    )
    code = models.CharField(max_length=100, verbose_name=_("کد"))
    discount_percent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("درصد تخفیف"),
    )
    max_limit_usage = models.PositiveIntegerField(
        default=10, verbose_name=_("حداکثر تعداد استفاده")
    )
    used_by = models.ManyToManyField(
        User,
        related_name="coupon_users",
        blank=True,
        verbose_name=_("استفاده شده توسط"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    expiration_date = models.DateTimeField(
        null=True, blank=True, verbose_name=_("تاریخ انقضا")
    )

    class Meta:
        verbose_name = _("کوپن")
        verbose_name_plural = _("کوپن‌ها")

    def validate(self, user):
        is_valid = False
        now = timezone.now()
        if not self.is_active:
            return is_valid, "این کوپن غیر فعال است"
        if not now < self.expiration_date:
            return is_valid, "این کوپن منقضی شده است"

        if not self.used_by.count() < self.max_limit_usage:
            return is_valid, "ظرفیت استفاده از این کوپن به پایان رسیده است"
        if self.used_by.filter(id=user.id).exists():
            return is_valid, "شما قبلا این کوپن را استفاده کرده اید"
        is_valid = True
        return is_valid, "کوپن با موفقیت اعمال شد"

    def __str__(self):
        return self.code
