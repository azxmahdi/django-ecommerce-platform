from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AddressModel,
    ShippingMethodModel,
    OrderModel,
    OrderItemModel,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItemModel
    extra = 1
    verbose_name = "آیتم سفارش"
    verbose_name_plural = "آیتم‌های سفارش"
    fields = (
        "product_variant",
        "quantity",
        "base_price",
        "final_price",
        "variant_discount_percent",
    )
    raw_id_fields = ("product_variant",)
    readonly_fields = ("final_price",)


@admin.register(OrderModel)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "status_display",
        "fulfillment_status",
        "total_price",
        "order_items_discount",
    )

    list_editable = ("status", "fulfillment_status")
    list_filter = ("status", "fulfillment_status", "created_date")
    search_fields = ("id", "user__phone")
    raw_id_fields = ("user", "address", "shipping_method", "coupon")
    date_hierarchy = "created_date"
    inlines = [OrderItemInline]
    list_select_related = ("user",)
    ordering = ("-created_date",)
    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات پایه",
            {"fields": ("user", "address", "status", "fulfillment_status")},
        ),
        ("کوپن و ارسال", {"fields": ("shipping_method", "coupon")}),
        ("قیمت و تخفیف", {"fields": ("total_price",)}),
    )

    @admin.display(description="وضعیت")
    def status_display(self, obj):
        return obj.get_status()["label"]


@admin.register(OrderItemModel)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product_variant",
        "quantity",
        "final_price",
    )
    readonly_fields = ("final_price",)

    list_filter = ("order__status", "created_date")
    search_fields = ("order__id", "product_variant__product_variant__name")
    raw_id_fields = ("order", "product_variant")
    list_per_page = 25

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"


@admin.register(AddressModel)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "user",
        "phone",
        "postal_code",
        "province",
        "city",
        "plaque",
        "unit",
        "full_address",
    )
    list_filter = ("province", "city")
    search_fields = (
        "first_name",
        "last_name",
        "phone",
        "postal_code",
        "province",
        "city",
        "user__phone",
    )
    ordering = ("-id",)
    readonly_fields = ("full_name", "full_address")

    fieldsets = (
        (
            "اطلاعات کاربر",
            {
                "fields": ("user", "first_name", "last_name", "phone"),
            },
        ),
        (
            "اطلاعات آدرس",
            {
                "fields": (
                    "province",
                    "city",
                    "address",
                    "postal_code",
                    "plaque",
                    "unit",
                ),
            },
        ),
        (
            "نمایش ترکیبی",
            {
                "fields": ("full_name", "full_address"),
            },
        ),
    )

    def full_name(self, obj):
        return obj.get_full_name()

    def full_address(self, obj):
        return obj.get_full_address()


@admin.register(ShippingMethodModel)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "estimated_days", "image_preview")
    search_fields = ("name",)
    ordering = ("-id",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='60' height='60' style='object-fit:cover;border-radius:6px;' />",
                obj.image.url,
            )
        return "بدون تصویر"
