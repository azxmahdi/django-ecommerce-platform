from django.contrib import admin

from .models import SupportInfoModel


@admin.register(SupportInfoModel)
class SupportInfoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "phone",
        "email",
        "headquarters_address",
    )

    list_filter = ("phone", "email", "created_date")
    search_fields = ("id", "email", "phone")
    date_hierarchy = "created_date"
    ordering = ("-created_date",)
    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات تماس",
            {
                "fields": ("phone", "email"),
            },
        ),
        (
            "دفتر مرکزی",
            {
                "fields": ("headquarters_address",),
            },
        ),
    )
