from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from django_summernote.admin import SummernoteModelAdmin

from .models import (
    ProductCategoryModel,
    ProductModel,
    CategoryFeatureModel,
    FeatureOptionModel,
    ProductFeatureModel,
    AttributeModel,
    AttributeValueModel,
    ProductVariantModel,
    ProductImageModel,
    SearchLogModel,
)


admin.site.site_header = "پنل مدیریت فروشگاه"
admin.site.site_title = "پنل مدیریت فروشگاه"
admin.site.index_title = "داشبورد مدیریت"


class CategoryFeatureInline(admin.TabularInline):
    model = CategoryFeatureModel
    extra = 1
    min_num = 1
    raw_id_fields = ("category",)


class FeatureOptionInline(admin.TabularInline):
    model = FeatureOptionModel
    extra = 1
    raw_id_fields = ("feature",)


class ProductFeatureInline(admin.TabularInline):
    model = ProductFeatureModel
    extra = 1
    raw_id_fields = ("feature", "option")


class ProductVariantInline(admin.TabularInline):

    model = ProductVariantModel
    extra = 1
    fields = ("attribute_value", "price", "stock")
    raw_id_fields = ("attribute_value",)
    show_change_link = True


@admin.register(ProductCategoryModel)
class ProductCategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = (
        "tree_actions",
        "indented_title",
        "slug_display",
    )
    list_display_links = ("indented_title",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CategoryFeatureInline]
    list_per_page = 20

    @admin.display()
    def slug_display(self, obj):
        return obj.slug


@admin.register(ProductModel)
class ProductAdmin(SummernoteModelAdmin):
    summernote_fields = ("description",)

    list_display = (
        "name",
        "category",
        "status",
        "published_date_display",
    )
    list_editable = ("status",)
    list_filter = ("status", "category")
    search_fields = ("name", "name_en", "slug")
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ("category",)
    date_hierarchy = "published_date"
    inlines = [ProductFeatureInline, ProductVariantInline]
    list_select_related = ("category",)
    ordering = ("-created_date",)
    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات پایه",
            {
                "fields": (
                    "category",
                    "name",
                    "name_en",
                    "slug",
                    "status",
                    "published_date",
                )
            },
        ),
        ("توضیحات و تصویر", {"fields": ("description", "image")}),
    )

    @admin.display(description="تاریخ انتشار")
    def published_date_display(self, obj):
        return obj.published_date


@admin.register(CategoryFeatureModel)
class CategoryFeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_required")
    list_filter = ("category", "is_required")
    search_fields = ("name", "category__name")
    raw_id_fields = ("category",)
    inlines = [FeatureOptionInline]
    list_per_page = 20


@admin.register(FeatureOptionModel)
class FeatureOptionAdmin(admin.ModelAdmin):
    list_display = ("value", "feature")
    list_filter = ("feature__category", "feature")
    search_fields = ("value",)
    raw_id_fields = ("feature",)
    list_per_page = 20


@admin.register(AttributeModel)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_per_page = 20


@admin.register(AttributeValueModel)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attribute", "value")
    list_filter = ("attribute",)
    search_fields = ("value",)
    raw_id_fields = ("attribute",)
    list_per_page = 20


@admin.register(ProductVariantModel)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "attribute_value",
        "stock",
        "price",
        "discount_percent",
    )
    list_filter = (
        "product__category",
        "product",
        "attribute_value__attribute",
    )
    search_fields = ("product__name", "attribute_value__value")
    readonly_fields = ("final_price",)
    raw_id_fields = ("product", "attribute_value")
    list_select_related = (
        "product",
        "attribute_value",
        "attribute_value__attribute",
    )
    list_per_page = 25
    fieldsets = (
        ("اطلاعات پایه", {"fields": ("product", "attribute_value", "stock")}),
        (
            "قیمت و تخفیف",
            {"fields": ("price", "discount_percent", "final_price")},
        ),
    )


@admin.register(ProductImageModel)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "file", "created_date")
    list_filter = ("created_date", "product")
    search_fields = ("product__name",)
    ordering = ("-created_date",)


@admin.register(SearchLogModel)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ("user", "query")
    list_filter = ("user__phone", "query")
    search_fields = ("user__phone", "query")
    readonly_fields = ("created_date", "updated_date")
    raw_id_fields = ("user",)
    list_select_related = ("user",)
    list_per_page = 25
    fieldsets = (
        (
            "اطلاعات جستجو",
            {
                "fields": ("user", "query"),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": ("created_date", "updated_date"),
            },
        ),
    )
