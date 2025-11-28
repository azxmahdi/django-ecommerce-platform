from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from common.models import TimeStampedModel

User = get_user_model()


class MessageType(models.IntegerChoices):
    BROADCAST = 1, _("انتشار عمومی")
    ORDER = 2, _("به‌روزرسانی سفارش")
    PERSONAL = 3, _("شخصی")


class MessageModel(TimeStampedModel):
    type = models.IntegerField(
        choices=MessageType.choices,
        default=MessageType.PERSONAL,
        verbose_name=_("نوع پیام"),
    )
    title = models.CharField(max_length=255, verbose_name=_("عنوان"))
    body = models.TextField(verbose_name=_("متن"))
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="messages",
        verbose_name=_("کاربر"),
    )
    order = models.ForeignKey(
        "order.OrderModel",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("سفارش"),
    )
    is_read = models.BooleanField(default=False, verbose_name=_("خوانده شده"))

    class Meta:
        verbose_name = _("پیام")
        verbose_name_plural = _("پیام‌ها")

    def __str__(self):
        return f"{self.get_type_display()} - {self.title}"


class UserMessageStatusModel(TimeStampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="message_statuses",
        verbose_name=_("کاربر"),
    )
    message = models.ForeignKey(
        MessageModel,
        on_delete=models.CASCADE,
        related_name="user_statuses",
        verbose_name=_("پیام"),
    )
    is_hidden = models.BooleanField(default=False, verbose_name=_("پنهان شده"))
    is_read = models.BooleanField(default=False, verbose_name=_("خوانده شده"))

    class Meta:
        unique_together = ("user", "message")
        ordering = ("-created_date",)
        verbose_name = _("وضعیت پیام کاربر")
        verbose_name_plural = _("وضعیت‌های پیام کاربران")
