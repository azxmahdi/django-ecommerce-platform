from collections import defaultdict
from typing import Dict, Any, List, Callable, Optional

from django.db.models import Count
from django.http import HttpRequest

from shop.models import (
    ProductCategoryModel,
    CategoryFeatureModel,
    ProductFeatureModel,
    AttributeValueModel,
)
from common.services.pagination_builders import build_pagination_items
from common.services.base_context_builders import BaseContextBuilder
from review.models import ProductCommentModel, CommentStatus


class ProductListContextBuilder(BaseContextBuilder):
    def _get_default_processors(self):
        return [
            self._add_querystring,
            self._add_current_filters,
            self._add_category_data,
            self._add_pagination,
        ]

    def get_base_data(self):
        return {}

    def _add_querystring(self):
        params = self.request.GET.copy()
        params.pop("page", None)
        self.context["querystring"] = params.urlencode()

    def _add_current_filters(self):
        filters = dict(self.request.GET.items())
        filters.pop("page", None)
        self.context["current_filters"] = filters

    def _add_category_data(self):
        filters = self.context.get("current_filters", {})
        category_slug = filters.get("category_slug")

        if category_slug:
            try:
                category = ProductCategoryModel.objects.get(slug=category_slug)
                if not category.is_last_level():
                    self.context["is_subcategories"] = True
                    self.context["subcategories"] = category.get_children()
                else:
                    self.context["is_subcategories"] = False

                self.context["features"] = CategoryFeatureModel.objects.filter(
                    category=category
                ).prefetch_related("options")
            except ProductCategoryModel.DoesNotExist:
                self._set_root_categories()
        else:
            self._set_root_categories()

    def _set_root_categories(self):
        self.context["is_subcategories"] = True
        self.context["subcategories"] = (
            ProductCategoryModel.objects.root_nodes()
        )
        self.context["features"] = []

    def _add_pagination(self):
        self.context["page_items"] = build_pagination_items(self.context)


from django.db.models import Prefetch

from collections import defaultdict
from django.db.models import Prefetch


class ProductDetailContextBuilder(BaseContextBuilder):
    def __init__(
        self,
        request: HttpRequest,
        base_context: Dict[str, Any] = None,
        **kwargs
    ):
        super().__init__(request, base_context, **kwargs)
        self.product = self.extra_data.get("product")

    def _get_default_processors(self) -> List[Callable]:
        return [
            self._add_product_features,
            self._add_extra_images,
            self._add_comments,
            self._add_grouped_attributes,
        ]

    def get_base_data(self):
        return {}

    def _add_product_features(self):
        if self.product:
            self.context["product_features"] = self.product.features.all()

    def _add_extra_images(self):
        if self.product:
            self.context["extra_images"] = self.product.product_images.all()

    def _add_comments(self):
        if self.product:
            # استفاده از کامنت‌های prefetch شده
            if hasattr(self.product, "prefetched_comments"):
                all_comments = self.product.prefetched_comments
            else:
                # fallback در صورت عدم prefetch
                all_comments = ProductCommentModel.objects.filter(
                    product=self.product, status=CommentStatus.APPROVED.value
                ).select_related("user")

            # ساختاردهی کامنت‌ها و پاسخ‌ها در حافظه
            comments_dict = {}
            root_comments = []

            # ایجاد دیکشنری برای دسترسی سریع به کامنت‌ها
            for comment in all_comments:
                comments_dict[comment.id] = comment
                # استفاده از نام متفاوت برای جلوگیری از تداخل
                comment._prefetched_replies = []

            # مرتبط کردن پاسخ‌ها به کامنت‌های والد
            for comment in all_comments:
                if comment.parent_id and comment.parent_id in comments_dict:
                    parent_comment = comments_dict[comment.parent_id]
                    parent_comment._prefetched_replies.append(comment)
                elif comment.parent_id is None:
                    root_comments.append(comment)

            # مرتب‌سازی بر اساس تاریخ
            root_comments.sort(key=lambda x: x.created_date, reverse=True)
            for comment in all_comments:
                comment._prefetched_replies.sort(key=lambda x: x.created_date)

            self.context["comments"] = root_comments

    def _add_grouped_attributes(self):
        if self.product:
            grouped_attributes = defaultdict(set)
            for variant in self.product.variants.all():
                if variant.stock > 0:
                    grouped_attributes[
                        variant.attribute_value.attribute.name
                    ].add(variant.attribute_value.value)

            self.context["grouped_attributes"] = {
                attr_name: sorted(values)
                for attr_name, values in grouped_attributes.items()
            }
