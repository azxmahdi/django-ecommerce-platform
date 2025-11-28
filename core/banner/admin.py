from django.contrib import admin

from .models import BannerModel


@admin.register(BannerModel)
class BannerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "file",
        "position",
        "product_category",
        "post_category",
        "order",
        "is_active",
        "created_date",
    )
    readonly_fields = ("created_date", "updated_date")

    list_editable = ("is_active", "position", "order")
    list_filter = ("is_active", "position", "created_date")
    search_fields = (
        "id",
        "title",
        "product_category__name",
        "post_category__name",
    )
    raw_id_fields = ("product_category", "post_category")
    date_hierarchy = "created_date"
    list_select_related = ("product_category", "post_category")
    ordering = ("position", "-created_date")
    list_per_page = 25

    fieldsets = (
        (
            "فایل و نام بنر",
            {
                "fields": ("file", "title"),
            },
        ),
        (
            "دسته‌بندی هدف",
            {
                "fields": ("product_category", "post_category"),
            },
        ),
        (
            "تنظیمات نمایش",
            {
                "fields": ("position", "order", "is_active"),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": ("created_date", "updated_date"),
            },
        ),
    )
