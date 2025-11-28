from django import template
from django.db.models import (
    Sum,
    Subquery,
    OuterRef,
    Exists,
    ExpressionWrapper,
    F,
    DecimalField,
)
from django.db.models.functions import Round
from django.core.cache import cache

from shop.models import (
    ProductCategoryModel,
    ProductModel,
    ProductStatusType,
    ProductVariantModel,
)
from shop.services.filters import ProductFilter
from order.models import OrderModel, OrderStatusType
from blog.models import PostModel


register = template.Library()


@register.inclusion_tag("includes/best-selling-products.html")
def best_selling_products():
    cached_data = cache.get("best_selling_products")
    if cached_data:
        return {"products": cached_data}

    lowest_variant = (
        ProductVariantModel.objects.filter(product=OuterRef("pk"))
        .order_by("price")
        .annotate(
            final_price=ExpressionWrapper(
                F("price") * (100 - F("discount_percent")) / 100,
                output_field=DecimalField(),
            )
        )
        .annotate(final_price=Round(F("final_price"), 2))
        .values("price", "discount_percent", "final_price")[:1]
    )
    products = (
        ProductModel.objects.annotate(
            has_variant=Exists(
                ProductVariantModel.objects.filter(product=OuterRef("pk"))
            )
        )
        .filter(status=ProductStatusType.PUBLISH.value, has_variant=True)
        .order_by("-total_sold")[:10]
    )

    products = products.annotate(
        price=Subquery(lowest_variant.values("price")),
        discount_percent=Subquery(lowest_variant.values("discount_percent")),
        final_price=Subquery(lowest_variant.values("final_price")),
    )

    cache.set("best_selling_products", products, 60 * 60 * 48)
    return {"products": products}


@register.inclusion_tag("includes/posts.html")
def posts():
    return {"posts": PostModel.objects.all().order_by("view_count")[:6]}


@register.inclusion_tag("includes/newest-products.html")
def newest_products():
    cached_data = cache.get("newest_products")
    if cached_data:
        return {"products": cached_data}

    lowest_variant = (
        ProductVariantModel.objects.filter(product=OuterRef("pk"))
        .order_by("price")
        .annotate(
            final_price=ExpressionWrapper(
                F("price") * (100 - F("discount_percent")) / 100,
                output_field=DecimalField(),
            )
        )
        .annotate(final_price=Round(F("final_price"), 2))
        .values("price", "discount_percent", "final_price")[:1]
    )
    products = (
        ProductModel.objects.annotate(
            has_variant=Exists(
                ProductVariantModel.objects.filter(product=OuterRef("pk"))
            )
        )
        .filter(status=ProductStatusType.PUBLISH.value, has_variant=True)
        .order_by("-created_date")[:10]
    )

    products = products.annotate(
        price=Subquery(lowest_variant.values("price")),
        discount_percent=Subquery(lowest_variant.values("discount_percent")),
        final_price=Subquery(lowest_variant.values("final_price")),
    )

    cache.set("newest_products", products, 60 * 60 * 48)
    return {"products": products}
