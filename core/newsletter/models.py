from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import TimeStampedModel


class NewsLetterModel(TimeStampedModel):
    email = models.EmailField(verbose_name=_("ایمیل"))

    class Meta:
        verbose_name = _("خبرنامه")
        verbose_name_plural = _("خبرنامه‌ها")

    def __str__(self):
        return self.email
