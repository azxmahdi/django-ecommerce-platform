from django.contrib import admin
from django.utils.html import format_html

from .models import PaymentGateway


@admin.register(PaymentGateway)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "display_name",
        "is_active",
        "order",
        "config",
        "image_preview",
    )
    search_fields = ("name",)
    ordering = ("-id",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='60' height='60' style='object-fit:cover;border-radius:6px;' />",
                obj.image.url,
            )
        return "بدون تصویر"

    image_preview.short_description = "تصویر"
