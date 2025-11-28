from django.contrib import admin

from .models import MessageModel, UserMessageStatusModel


@admin.register(MessageModel)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "type",
        "title",
        "body",
        "order",
        "is_read",
    )

    list_editable = ("is_read",)
    list_filter = ("type", "created_date")
    search_fields = ("id", "title", "user__phone")
    raw_id_fields = ("user", "order")
    date_hierarchy = "created_date"
    list_select_related = ("user",)
    ordering = ("-created_date",)
    list_per_page = 25

    fieldsets = (
        ("اطلاعات پایه", {"fields": ("type", "title", "body")}),
        ("ارتباطات", {"fields": ("user", "order")}),
        ("وضعیت", {"fields": ("is_read",)}),
    )
    readonly_fields = ("created_date",)


@admin.register(UserMessageStatusModel)
class UserMessageStatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "message",
        "is_read",
        "is_hidden",
        "created_date",
        "updated_date",
    )
    list_editable = ("is_read", "is_hidden")
    list_filter = ("is_read", "is_hidden", "created_date")
    search_fields = ("id", "user__phone", "message__title")
    raw_id_fields = ("user", "message")
    date_hierarchy = "created_date"
    list_select_related = ("user", "message")
    ordering = ("-created_date",)
    list_per_page = 25

    fieldsets = (
        ("ارتباطات", {"fields": ("user", "message")}),
        ("وضعیت", {"fields": ("is_read", "is_hidden")}),
        ("زمان‌ها", {"fields": ("created_date", "updated_date")}),
    )

    readonly_fields = ("created_date", "updated_date")
