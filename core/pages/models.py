from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from common.models import TimeStampedModel


class StaticPageModel(TimeStampedModel):
    slug = models.SlugField(
        max_length=100, unique=True, verbose_name=_("اسلاگ")
    )
    title = models.CharField(max_length=200, verbose_name=_("عنوان"))
    content = models.TextField(verbose_name=_("محتوا"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))

    class Meta:
        ordering = ["title"]
        verbose_name = _("صفحه استاتیک")
        verbose_name_plural = _("صفحات استاتیک")

    def get_absolute_url(self):
        return reverse("pages:static-page", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title
