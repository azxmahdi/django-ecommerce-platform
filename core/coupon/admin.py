from django.contrib import admin
from django.utils import timezone

from .models import CouponModel


from django.contrib import admin
from django.utils import timezone
from .models import CouponModel


@admin.register(CouponModel)
class CouponModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "code",
        "discount_percent",
        "max_limit_usage",
        "used_count",
        "is_active",
        "expiration_date",
        "is_expired",
        "created_date",
    )

    list_editable = ("is_active", "max_limit_usage", "discount_percent")
    list_filter = ("is_active", "created_date", "expiration_date")
    search_fields = ("code", "user__phone")
    date_hierarchy = "created_date"
    list_select_related = ("user",)
    ordering = ("-created_date",)
    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات پایه",
            {
                "fields": (
                    "code",
                    "discount_percent",
                    "max_limit_usage",
                    "is_active",
                )
            },
        ),
        ("تاریخ‌ها", {"fields": ("expiration_date",)}),
        (
            "کاربران استفاده‌کننده",
            {
                "fields": ("used_by",),
            },
        ),
    )

    filter_horizontal = ("used_by",)
    readonly_fields = ("created_date", "status_display", "user_display")

    @admin.display(description="تعداد استفاده")
    def used_count(self, obj):
        return obj.used_by.count()

    @admin.display(description="وضعیت انقضا", boolean=True)
    def is_expired(self, obj):
        if not obj.expiration_date:
            return False
        return timezone.now() > obj.expiration_date

    @admin.display(description="وضعیت")
    def status_display(self, obj):
        if not obj.is_active:
            return "غیرفعال"
        if self.is_expired(obj):
            return "منقضی شده"
        if obj.used_by.count() >= obj.max_limit_usage:
            return "تکمیل ظرفیت"
        return "فعال"

    @admin.display(description="کاربر ایجادکننده")
    def user_display(self, obj):
        if obj.user:
            return (
                f"{obj.user.phone} ({obj.user.get_full_name() or 'بدون نام'})"
            )
        return "سیستمی"

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            fieldsets = (
                (
                    "اطلاعات پایه",
                    {
                        "fields": (
                            "user_display",
                            "code",
                            "discount_percent",
                            "max_limit_usage",
                            "is_active",
                        )
                    },
                ),
                ("تاریخ‌ها", {"fields": ("expiration_date", "created_date")}),
                (
                    "کاربران استفاده‌کننده",
                    {
                        "fields": ("used_by",),
                    },
                ),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)
