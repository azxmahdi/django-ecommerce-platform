from django.db.models import (
    Q,
    Exists,
    OuterRef,
    Subquery,
    ExpressionWrapper,
    DecimalField,
    F,
)
from django.db.models.functions import Round

from common.services.base_filters import BaseFilter
from shop.models import (
    ProductFeatureModel,
    ProductCategoryModel,
    ProductVariantModel,
    ProductStatusType,
)


class ProductFilter(BaseFilter):
    def _get_filter_methods(self):
        return [
            self._filter_base_conditions,
            self._annotate_variant_fields,
            self._filter_by_category,
            self._filter_by_price,
            self._filter_by_search,
            self._filter_by_features,
            self._order,
        ]

    def _filter_base_conditions(self, queryset):
        queryset = queryset.annotate(
            has_variant=Exists(
                ProductVariantModel.objects.filter(
                    product=OuterRef("pk"), stock__gt=0
                )
            )
        ).filter(status=ProductStatusType.PUBLISH.value, has_variant=True)
        return queryset

    def _filter_by_features(self, queryset):
        for key, values in self.params.lists():
            if key.startswith("feature_"):
                feature_id = key.split("_", 1)[1]
                values = [v for v in values if v.strip()]
                if not values:
                    continue
                subquery = ProductFeatureModel.objects.filter(
                    product_id=OuterRef("id"), feature_id=feature_id
                ).filter(Q(option__value__in=values) | Q(value__in=values))
                queryset = queryset.annotate(
                    **{f"has_feature_{feature_id}": Exists(subquery)}
                ).filter(**{f"has_feature_{feature_id}": True})
        return queryset

    def _filter_by_search(self, queryset):
        if q := self.params.get("q"):
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )
        return queryset

    def _filter_by_price(self, queryset):
        if min_price := self.params.get("min_price"):
            queryset = queryset.filter(price__gte=min_price)
        if max_price := self.params.get("max_price"):
            queryset = queryset.filter(price__lte=max_price)
        return queryset

    def _filter_by_category(self, queryset):
        if slug := self.params.get("category_slug"):
            try:
                cat = ProductCategoryModel.objects.get(slug=slug)
                subtree = cat.get_descendants(include_self=True)
                queryset = queryset.filter(category__in=subtree)
            except ProductCategoryModel.DoesNotExist:
                pass
        return queryset

    def _order(self, queryset):
        order_by = self.params.get("order_by")
        if order_by and order_by in [
            "-created_date",
            "-total_sold",
            "-price",
            "price",
        ]:
            return queryset.order_by(order_by)
        return queryset

    def _annotate_variant_fields(self, queryset):
        lowest_variant = (
            ProductVariantModel.objects.filter(product=OuterRef("pk"))
            .order_by("price")
            .annotate(
                final_price_calc=ExpressionWrapper(
                    F("price") * (100 - F("discount_percent")) / 100,
                    output_field=DecimalField(),
                )
            )
            .annotate(final_price_calc=Round(F("final_price_calc"), 2))
            .values("price", "discount_percent", "final_price_calc")[:1]
        )

        return queryset.annotate(
            price=Subquery(lowest_variant.values("price")),
            discount_percent=Subquery(
                lowest_variant.values("discount_percent")
            ),
            final_price=Subquery(lowest_variant.values("final_price_calc")),
        )
