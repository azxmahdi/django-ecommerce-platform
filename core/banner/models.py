from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from common.models import TimeStampedModel


class BannerPosition(models.IntegerChoices):
    MAIN = 1, _("بنر اصلی")
    SMALL = 2, _("بنر کوچک")
    SIDEBAR = 4, _("بنر کنار دسته‌بندی محصولات")
    CATEGORY = 5, _("بنر دسته بندی محصولات")


class BannerModel(TimeStampedModel):
    title = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("عنوان")
    )
    file = models.ImageField(upload_to="banners/", verbose_name=_("فایل"))

    product_category = models.ForeignKey(
        "shop.ProductCategoryModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="banners",
        verbose_name=_("دسته‌بندی محصول"),
    )
    post_category = models.ForeignKey(
        "blog.PostCategoryModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="banners",
        verbose_name=_("دسته‌بندی پست"),
    )
    order = models.PositiveIntegerField(verbose_name=_("ترتیب"))

    position = models.IntegerField(
        choices=BannerPosition.choices, verbose_name=_("محل قرارگیری")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))

    class Meta:
        ordering = ["position", "order"]
        verbose_name = _("بنر")
        verbose_name_plural = _("بنرها")

    def get_position(self):
        return {
            "id": self.position,
            "title": BannerPosition(self.position).name,
            "label": BannerPosition(self.position).label,
        }

    def get_target_url(self):
        if self.product_category:
            return (
                reverse("shop:product-list")
                + f"?category_slug={self.product_category.slug}"
            )
        elif self.post_category:
            return (
                reverse("blog:post-list")
                + f"?category_slug={self.post_category.slug}"
            )
        return "#"
