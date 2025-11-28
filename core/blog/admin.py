from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import PostModel, PostCategoryModel


@admin.register(PostModel)
class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ("content",)
    list_display = (
        "id",
        "title",
        "slug",
        "status",
        "view_count",
        "published_date",
        "created_date",
    )
    readonly_fields = ("created_date", "updated_date", "author")

    list_editable = ("status",)
    list_filter = ("status", "author", "published_date", "created_date")
    search_fields = ("id", "title", "slug", "content")
    raw_id_fields = ("author", "category")
    date_hierarchy = "published_date"
    list_select_related = ("author",)
    ordering = ("-published_date",)
    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": ("title", "slug", "content", "image"),
            },
        ),
        (
            "دسته‌بندی و نویسنده",
            {
                "fields": ("author", "category"),
            },
        ),
        (
            "تنظیمات انتشار",
            {
                "fields": ("status", "view_count", "published_date"),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": ("created_date", "updated_date"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user.user_profile
        super().save_model(request, obj, form, change)


@admin.register(PostCategoryModel)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "created_date",
    )
    readonly_fields = ("created_date", "updated_date")

    list_filter = ("created_date",)
    search_fields = ("id", "name", "slug")
    ordering = ("-created_date",)
    date_hierarchy = "created_date"
    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": ("name", "slug"),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": ("created_date", "updated_date"),
            },
        ),
    )
