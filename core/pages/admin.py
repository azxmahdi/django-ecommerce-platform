from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import StaticPageModel


@admin.register(StaticPageModel)
class StaticPageAdmin(SummernoteModelAdmin):
    summernote_fields = ("content",)
    list_display = (
        "id",
        "title",
        "slug",
        "is_active",
        "created_date",
        "updated_date",
    )
    list_filter = ("is_active", "created_date")
    search_fields = ("title", "slug", "content")
    ordering = ("-created_date",)
    date_hierarchy = "created_date"
    list_per_page = 25
    readonly_fields = ("created_date", "updated_date")

    fieldsets = (
        (
            "اطلاعات صفحه",
            {
                "fields": ("title", "slug", "content"),
            },
        ),
        (
            "وضعیت",
            {
                "fields": ("is_active",),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": ("created_date", "updated_date"),
            },
        ),
    )
