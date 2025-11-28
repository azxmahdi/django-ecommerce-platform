from django.contrib import admin

from .models import ContactModel


@admin.register(ContactModel)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "phone",
        "email",
        "message",
    )

    list_filter = ("email", "phone", "created_date")
    search_fields = ("id", "name", "email", "phone")
    date_hierarchy = "created_date"
    ordering = ("-created_date",)
    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات تماس",
            {
                "fields": ("name", "phone", "email"),
            },
        ),
        (
            "پیام کاربر",
            {
                "fields": ("message",),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": ("created_date", "updated_date"),
            },
        ),
    )
