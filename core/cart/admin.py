from django.contrib import admin
from .models import CartModel, CartItemModel


class CartItemInline(admin.TabularInline):
    model = CartItemModel
    extra = 1
    fields = ("product_variant", "quantity")
    autocomplete_fields = ("product_variant",)


@admin.register(CartModel)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_date", "updated_date")
    list_filter = ("created_date", "updated_date")
    search_fields = ("user__phone",)
    inlines = [CartItemInline]
    readonly_fields = ("created_date", "updated_date")
    date_hierarchy = "created_date"
    ordering = ("-created_date",)

    fieldsets = (
        (
            "اطلاعات کاربر",
            {
                "fields": ("user",),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": ("created_date", "updated_date"),
            },
        ),
    )


@admin.register(CartItemModel)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cart",
        "product_variant",
        "quantity",
        "created_date",
    )
    list_filter = ("created_date", "cart__user")
    search_fields = (
        "cart__user__phone",
        "product_variant__product__name",
    )
    readonly_fields = ("created_date", "updated_date")
    raw_id_fields = ("cart", "product_variant")
    date_hierarchy = "created_date"
    ordering = ("-created_date",)

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": ("cart", "product_variant", "quantity"),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": ("created_date", "updated_date"),
            },
        ),
    )
