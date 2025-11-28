import re
from datetime import timedelta

from django.utils import timezone
from django.db.models import Q, Exists, OuterRef
from shop.models import ProductFeatureModel, ProductCategoryModel
from common.services.base_filters import BaseFilter


class PostFilter(BaseFilter):
    def _get_filter_methods(self):
        return [
            self._filter_by_search,
            self._filter_by_is_hot,
            self._filter_by_category,
            self._order,
        ]

    def _filter_by_category(self, queryset):
        if category_slug := self.params.get("category_slug", "").strip():
            slugs = [
                slug.strip()
                for slug in category_slug.split(",")
                if slug.strip()
            ]
            queryset = queryset.filter(category__slug__in=slugs).distinct()
        return queryset

    def _filter_by_search(self, queryset):
        if q := self.params.get("q"):
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(content__icontains=q)
            )
        return queryset

    def _filter_by_is_hot(self, queryset):
        if self.params.get("is_hot"):
            queryset = queryset.filter(
                published_date__gte=timezone.now() - timedelta(days=1),
                view_count__gt=100,
            )
        return queryset

    def _order(self, queryset):
        if order_by := self.params.get("order_by"):
            queryset = queryset.order_by(order_by)
        return queryset
