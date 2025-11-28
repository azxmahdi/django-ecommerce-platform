from django.db import models
from django.utils.translation import gettext_lazy as _


class WishlistProductModel(models.Model):
    user = models.ForeignKey(
        "account.CustomUser", on_delete=models.PROTECT, verbose_name=_("کاربر")
    )
    product = models.ForeignKey(
        "shop.ProductModel",
        on_delete=models.CASCADE,
        related_name="in_wishlists",
        verbose_name=_("محصول"),
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = _("محصول موردعلاقه")
        verbose_name_plural = _("محصولات موردعلاقه")

    def __str__(self):
        return self.product.name
