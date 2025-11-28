from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import FAQCategoryModel, FAQModel


@admin.register(FAQCategoryModel)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title",)
    ordering = ("title",)
    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات دسته‌بندی",
            {
                "fields": ("title",),
            },
        ),
    )


@admin.register(FAQModel)
class FAQAdmin(SummernoteModelAdmin):
    summernote_fields = ("answer",)
    list_display = (
        "id",
        "question",
        "category",
        "is_active",
        "created_date",
        "updated_date",
    )
    list_filter = ("category", "is_active", "created_date")
    search_fields = ("question", "answer")
    ordering = ("-created_date",)
    date_hierarchy = "created_date"
    list_per_page = 25
    readonly_fields = ("created_date", "updated_date")

    fieldsets = (
        (
            "اطلاعات سوال",
            {
                "fields": ("category", "question", "answer"),
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
