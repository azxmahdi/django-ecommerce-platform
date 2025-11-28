from django.db import models
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from common.models import TimeStampedModel


User = get_user_model()


class CommentStatus(models.IntegerChoices):
    PENDING = 1, _("در انتظار تأیید")
    APPROVED = 2, _("تأیید شده")
    REJECTED = 3, _("رد شده")


class ProductCommentModel(TimeStampedModel):
    product = models.ForeignKey(
        "shop.ProductModel",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("محصول"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="product_comments",
        verbose_name=_("کاربر"),
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name=_("والد"),
    )
    is_recommended = models.BooleanField(verbose_name=_("توصیه می‌کنم"))
    title = models.CharField(max_length=400, verbose_name=_("عنوان"))
    text = models.TextField(verbose_name=_("متن"))
    status = models.IntegerField(
        choices=CommentStatus.choices,
        default=CommentStatus.PENDING,
        verbose_name=_("وضعیت"),
    )
    likes = models.PositiveIntegerField(
        default=0, verbose_name=_("تعداد پسندیدن")
    )
    dislikes = models.PositiveIntegerField(
        default=0, verbose_name=_("تعداد نپسندیدن")
    )

    @property
    def prefetched_replies(self):
        """Property برای دسترسی به پاسخ‌های کش شده"""
        if hasattr(self, "_prefetched_replies"):
            return self._prefetched_replies
        else:
            # fallback به کوئری دیتابیس
            return self.replies.filter(
                status=CommentStatus.APPROVED.value
            ).select_related("user")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "parent"],
                name="unique_reply_per_user_per_comment",
            )
        ]
        indexes = [
            models.Index(fields=["product", "status", "parent"]),
            models.Index(fields=["status", "parent", "created_date"]),
            models.Index(fields=["user", "created_date"]),
        ]
        verbose_name = _("نظر")
        verbose_name_plural = _("نظرات")

    def __str__(self):
        return f"{self.user} - {self.text[:30]}"
