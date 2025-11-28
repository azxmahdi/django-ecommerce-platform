from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import TimeStampedModel


class FAQCategoryModel(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("عنوان"))

    class Meta:
        verbose_name = _("دسته‌بندی سوالات متداول")
        verbose_name_plural = _("دسته‌بندی‌های سوالات متداول")

    def __str__(self):
        return self.title


class FAQModel(TimeStampedModel):
    category = models.ForeignKey(
        FAQCategoryModel,
        on_delete=models.CASCADE,
        related_name="faqs",
        verbose_name=_("دسته‌بندی"),
    )
    question = models.CharField(max_length=400, verbose_name=_("سوال"))
    answer = models.TextField(verbose_name=_("پاسخ"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))

    class Meta:
        verbose_name = _("سوال متداول")
        verbose_name_plural = _("سوالات متداول")

    def __str__(self):
        return self.question
