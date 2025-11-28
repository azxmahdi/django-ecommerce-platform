from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from common.models import TimeStampedModel

User = get_user_model()


class CartModel(TimeStampedModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("کاربر")
    )

    class Meta:
        verbose_name = _("سبد خرید")
        verbose_name_plural = _("سبدهای خرید")


class CartItemModel(TimeStampedModel):
    cart = models.ForeignKey(
        CartModel,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name=_("سبد خرید"),
    )

    product_variant = models.ForeignKey(
        "shop.ProductVariantModel",
        on_delete=models.PROTECT,
        verbose_name=_("تنوع محصول"),
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name=_("تعداد"))

    class Meta:
        verbose_name = _("آیتم سبد خرید")
        verbose_name_plural = _("آیتم‌های سبد خرید")
