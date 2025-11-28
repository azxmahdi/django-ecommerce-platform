from django.contrib import admin

from .models import WishlistProductModel


@admin.register(WishlistProductModel)
class WishlistProductAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "created_display")
    list_filter = ("user", "product")
    search_fields = ("user__username", "user__email", "product__name")
    ordering = ("-id",)

    def created_display(self, obj):
        return obj.id

    created_display.short_description = "ترتیب ایجاد"

    class Meta:
        verbose_name = "محصول علاقه‌مندی"
        verbose_name_plural = "محصولات علاقه‌مندی کاربران"
