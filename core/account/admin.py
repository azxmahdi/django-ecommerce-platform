from django.contrib import admin
from .models import CustomUser, ProfileModel


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "phone",
        "type",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_date",
        "updated_date",
    )
    list_editable = ("is_active", "is_staff", "is_superuser")
    list_filter = (
        "type",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_date",
    )
    search_fields = ("id", "phone")
    date_hierarchy = "created_date"
    ordering = ("-created_date",)
    list_per_page = 25

    fieldsets = (
        ("اطلاعات کاربری", {"fields": ("phone", "type")}),
        ("دسترسی‌ها", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("زمان‌ها", {"fields": ("created_date", "updated_date")}),
    )

    readonly_fields = ("created_date", "updated_date")


@admin.register(ProfileModel)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "first_name",
        "last_name",
        "full_name",
        "image",
        "created_date",
        "updated_date",
    )
    list_filter = ("created_date", "updated_date")
    search_fields = ("user__phone", "first_name", "last_name")
    raw_id_fields = ("user",)
    date_hierarchy = "created_date"
    ordering = ("-created_date",)
    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات پایه",
            {"fields": ("user", "first_name", "last_name", "image")},
        ),
        ("نمایش ترکیبی", {"fields": ("full_name",)}),
        ("زمان‌ها", {"fields": ("created_date", "updated_date")}),
    )

    readonly_fields = ("full_name", "created_date", "updated_date")

    def full_name(self, obj):
        return obj.full_name
