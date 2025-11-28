from django.contrib import admin
from django.utils.html import format_html

from .models import SiteInfoModel, SiteResourceModel


@admin.register(SiteInfoModel)
class SiteInfoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "store_name",
        "logo",
        "support_email",
        "support_phone",
        "head_office_address",
        "support_hours",
        "created_date",
        "updated_date",
    )
    readonly_fields = ("created_date", "updated_date")

    list_editable = ("support_email", "support_phone", "support_hours")
    list_filter = ("created_date", "updated_date")
    search_fields = (
        "store_name",
        "support_email",
        "support_phone",
        "head_office_address",
    )
    date_hierarchy = "created_date"
    ordering = ("store_name",)
    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات فروشگاه",
            {
                "fields": ("store_name", "logo"),
            },
        ),
        (
            "اطلاعات تماس",
            {
                "fields": ("support_email", "support_phone", "support_hours"),
            },
        ),
        (
            "آدرس دفتر مرکزی",
            {
                "fields": ("head_office_address",),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": ("created_date", "updated_date"),
            },
        ),
    )


@admin.register(SiteResourceModel)
class SiteResourceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "url",
        "image_preview",
        "created_date",
        "updated_date",
    )
    readonly_fields = ("created_date", "updated_date")

    list_editable = ("url",)
    list_filter = ("type", "created_date", "updated_date")
    search_fields = ("url",)
    date_hierarchy = "created_date"
    ordering = ("type",)
    list_per_page = 25

    fieldsets = (
        (
            "نوع منبع",
            {
                "fields": ("type",),
            },
        ),
        (
            "جزئیات منبع",
            {
                "fields": ("url", "logo"),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": ("created_date", "updated_date"),
            },
        ),
    )

    def image_preview(self, obj):
        if obj.logo:
            return format_html(
                "<img src='{}' width='60' height='60' style='object-fit:cover;border-radius:6px;' />",
                obj.logo.url,
            )
        return "بدون لوگو"

    image_preview.short_description = "لوگو"
