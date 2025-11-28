from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from account.models import ProfileModel
from common.models import TimeStampedModel


class PostCategoryModel(TimeStampedModel):
    name = models.CharField(max_length=225, verbose_name=_("نام"))
    slug = models.SlugField(unique=True, verbose_name=_("اسلاگ"))

    class Meta:
        verbose_name = _("دسته‌بندی پست")
        verbose_name_plural = _("دسته‌بندی‌های پست")

    def __str__(self):
        return self.name


class PostModel(TimeStampedModel):
    title = models.CharField(max_length=225, verbose_name=_("عنوان"))
    slug = models.SlugField(unique=True, verbose_name=_("اسلاگ"))
    content = models.TextField(verbose_name=_("محتوا"))
    image = models.ImageField(upload_to="blog/images", verbose_name=_("تصویر"))
    author = models.ForeignKey(
        ProfileModel, on_delete=models.CASCADE, verbose_name=_("نویسنده")
    )
    category = models.ManyToManyField(
        PostCategoryModel, related_name="posts", verbose_name=_("دسته‌بندی")
    )
    status = models.BooleanField(default=False, verbose_name=_("وضعیت"))
    view_count = models.DecimalField(
        decimal_places=0,
        max_digits=6,
        default=0,
        verbose_name=_("تعداد بازدید"),
    )
    published_date = models.DateTimeField(verbose_name=_("تاریخ انتشار"))

    class Meta:
        ordering = ("-published_date",)
        verbose_name = _("پست")
        verbose_name_plural = _("پست‌ها")

    def get_summary(self):
        return self.content[:100]

    def __str__(self):
        return self.title
