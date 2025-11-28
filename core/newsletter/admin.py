from django.contrib import admin

from .models import NewsLetterModel


@admin.register(NewsLetterModel)
class NewsLetterAdmin(admin.ModelAdmin):
    list_display = ("id", "email")

    list_filter = ("email", "created_date")
    search_fields = ("id", "email")
    date_hierarchy = "created_date"
    ordering = ("-created_date",)
    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات کاربر",
            {
                "fields": ("email",),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": ("created_date", "updated_date"),
            },
        ),
    )
