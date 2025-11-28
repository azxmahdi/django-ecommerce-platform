from decimal import Decimal
from model_utils import FieldTracker
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

from common.validators import phone_validator
from common.models import TimeStampedModel
from payment.models import PaymentModel
from .managers import OrderManager

User = get_user_model()


class AddressModel(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("کاربر")
    )
    first_name = models.CharField(max_length=225, verbose_name=_("نام"))
    last_name = models.CharField(
        max_length=225, verbose_name=_("نام خانوادگی")
    )
    phone = models.CharField(
        max_length=12, validators=[phone_validator], verbose_name=_("تلفن")
    )

    postal_code = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^\d{10}$", message="کد پستی باید دقیقا ۱۰ رقم باشد."
            )
        ],
        verbose_name=_("کد پستی"),
    )
    address = models.TextField(verbose_name=_("آدرس"))
    province = models.CharField(max_length=300, verbose_name=_("استان"))
    city = models.CharField(max_length=300, verbose_name=_("شهر"))
    plaque = models.CharField(max_length=10, verbose_name=_("پلاک"))
    unit = models.PositiveIntegerField(
        blank=True, null=True, verbose_name=_("واحد")
    )

    class Meta:
        verbose_name = _("آدرس")
        verbose_name_plural = _("آدرس‌ها")

    def __str__(self):
        return self.postal_code

    def get_full_address(self):
        return (
            f"استان { self.province } شهر { self.city } - {self.address} - پلاک { self.plaque }"
            + f"- واحد { self.unit }"
            if self.unit is not None
            else ""
        )

    def get_full_name(self):
        return f"{ self.first_name } { self.last_name }"


class ShippingMethodModel(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("نام"))
    image = models.ImageField(
        upload_to="shipping-method/", verbose_name=_("تصویر")
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name=_("هزینه")
    )
    estimated_days = models.PositiveIntegerField(
        verbose_name=_("زمان تقریبی (روز)")
    )

    class Meta:
        verbose_name = _("روش ارسال")
        verbose_name_plural = _("روش‌های ارسال")


class OrderStatusType(models.IntegerChoices):
    PENDING = 1, _("در انتظار پرداخت")
    SUCCESS = 2, _("پرداخت شده")
    FAILED = 3, _("لغو شده")


class FulfillmentStatus(models.IntegerChoices):
    PENDING_APPROVAL = 1, _("در انتظار تایید")
    PROCESSING = 2, _("در حال پردازش")
    SHIPPED = 3, _("ارسال شده")
    DELIVERED = 4, _("تحویل داده شده")
    RETURNED = 5, _("مرجوع شده")


class OrderModel(TimeStampedModel):
    user = models.ForeignKey(
        "account.CustomUser", on_delete=models.PROTECT, verbose_name=_("کاربر")
    )

    address = models.ForeignKey(
        AddressModel,
        on_delete=models.PROTECT,
        related_name="order",
        verbose_name=_("آدرس"),
    )

    total_price = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=0,
        verbose_name=_("مجموع قیمت"),
    )
    order_items_discount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=0,
        verbose_name=_("تخفیف آیتم‌های سفارش"),
    )
    shipping_method = models.ForeignKey(
        ShippingMethodModel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name=_("روش ارسال"),
    )
    tracking_number = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("شماره پیگیری"),
    )

    coupon = models.ForeignKey(
        "coupon.CouponModel",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("کوپن"),
    )
    status = models.IntegerField(
        choices=OrderStatusType.choices,
        default=OrderStatusType.PENDING.value,
        verbose_name=_("وضعیت"),
    )
    fulfillment_status = models.IntegerField(
        choices=FulfillmentStatus.choices,
        null=True,
        blank=True,
        verbose_name=_("وضعیت تکمیل"),
    )
    tracker = FieldTracker()

    objects = OrderManager()

    class Meta:
        verbose_name = _("سفارش")
        verbose_name_plural = _("سفارش‌ها")

    def save(self, *args, **kwargs):
        if (
            self.status == OrderStatusType.SUCCESS
            and self.fulfillment_status is None
            and self.pk is not None
        ):

            self.fulfillment_status = FulfillmentStatus.PENDING_APPROVAL

        super().save(*args, **kwargs)

    def calculate_total_price(self):
        return sum(
            item.final_price * item.quantity for item in self.order_items.all()
        )

    def calculate_total_price_with_coupon(self):
        total_price = self.calculate_total_price()
        if self.coupon:
            return round(
                total_price
                - (total_price * Decimal(self.coupon.discount_percent / 100))
            )
        else:
            return total_price

    def calculate_discount_coupon(self):
        if self.coupon:
            return round(
                self.calculate_total_price()
                * Decimal(self.coupon.discount_percent / 100)
            )
        return 0

    @property
    def total_discounts(self):
        return self.order_items_discount + self.calculate_discount_coupon()

    def get_status(self):
        return {
            "id": self.status,
            "title": OrderStatusType(self.status).name,
            "label": OrderStatusType(self.status).label,
        }

    def get_fulfillment_status(self):
        if self.fulfillment_status is None:
            return None
        return {
            "id": self.fulfillment_status,
            "title": FulfillmentStatus(self.fulfillment_status).name,
            "label": FulfillmentStatus(self.fulfillment_status).label,
        }

    @property
    def final_price(self):

        if self.coupon:
            return round(
                self.total_price
                - (
                    self.total_price
                    * Decimal(self.coupon.discount_percent / 100)
                )
            )
        else:
            return self.total_price

    def get_amount(self):
        return (
            self.calculate_total_price_with_coupon()
            + self.shipping_method.price
        )


class OrderItemModel(TimeStampedModel):
    order = models.ForeignKey(
        OrderModel,
        on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name=_("سفارش"),
    )
    product_variant = models.ForeignKey(
        "shop.ProductVariantModel",
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name=_("تنوع محصول"),
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name=_("تعداد"))

    base_price = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name=_("قیمت پایه")
    )
    variant_discount_percent = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("درصد تخفیف"),
    )

    class Meta:
        verbose_name = _("آیتم سفارش")
        verbose_name_plural = _("آیتم‌های سفارش")

    @property
    def final_price(self):
        if self.base_price is None:
            return Decimal(0)
        return round(
            self.base_price
            * (1 - Decimal(self.variant_discount_percent) / 100)
        )

    def __str__(self):
        return f"{self.product_variant.product.name} - {self.order.id}"

    def total_discounts(self):
        return (self.base_price * self.quantity) * Decimal(
            self.variant_discount_percent / 100
        )

    @property
    def total_base_price(self):
        return self.base_price * self.quantity

    @property
    def total_price(self):
        return self.final_price * self.quantity
