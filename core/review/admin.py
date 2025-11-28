from django.contrib import admin
from django.utils.html import format_html

from .models import ProductCommentModel, CommentStatus


@admin.register(ProductCommentModel)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "title",
        "status_badge",
        "created_date_display",
    )
    list_display_links = ("title",)
    list_filter = ("status", "created_date", "product__category")
    search_fields = ("text", "user__username", "product__name")
    raw_id_fields = ("user", "product", "parent")
    actions = ["approve_comments", "reject_comments"]
    list_per_page = 25
    date_hierarchy = "created_date"

    fieldsets = (
        ("اطلاعات پایه", {"fields": ("user", "product", "parent", "status")}),
        ("محتوای کامنت", {"fields": ("title", "text", "is_recommended")}),
        ("آمار", {"fields": ("likes", "dislikes")}),
    )

    @admin.display(description="تاریخ ایجاد")
    def created_date_display(self, obj):
        return obj.created_date.strftime("%Y-%m-%d %H:%M")

    @admin.display(description="وضعیت")
    def status_badge(self, obj):
        status_colors = {
            CommentStatus.PENDING: "orange",
            CommentStatus.APPROVED: "green",
            CommentStatus.REJECTED: "red",
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 8px; border-radius: 4px;">{}</span>',
            status_colors[obj.status],
            obj.get_status_display(),
        )

    @admin.action(description="تأیید کامنت‌های انتخاب شده")
    def approve_comments(self, request, queryset):
        updated = queryset.update(status=CommentStatus.APPROVED)
        self.message_user(request, f"{updated} کامنت با موفقیت تأیید شد.")

    @admin.action(description="رد کامنت‌های انتخاب شده")
    def reject_comments(self, request, queryset):
        updated = queryset.update(status=CommentStatus.REJECTED)
        self.message_user(request, f"{updated} کامنت با موفقیت رد شد.")
