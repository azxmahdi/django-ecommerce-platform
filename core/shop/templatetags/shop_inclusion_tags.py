from django import template
from django.db.models import Sum, Subquery, OuterRef
from django.core.cache import cache

from shop.models import (
    ProductCategoryModel,
    ProductModel,
    ProductStatusType,
    ProductVariantModel,
)
from order.models import OrderModel, OrderStatusType
from blog.models import PostModel

register = template.Library()


@register.inclusion_tag("includes/category-banners.html")
def category_banners():
    slugs = ["رژلب", "مردانه"]
    categories = ProductCategoryModel.objects.filter(slug__in=slugs).only(
        "slug"
    )
    lipstick_category = categories.filter(slug=slugs[0]).first()
    men_clothing_category = categories.filter(slug=slugs[1]).first()
    return {
        "lipstick": lipstick_category,
        "men_clothing": men_clothing_category,
    }


@register.inclusion_tag("includes/category.html")
def category():
    slugs = [
        "پیراهن-مردانه",
        "گوشی-هوشمند",
        "ماشین-اسباب-بازی",
        "ساعت-هوشمند",
        "مانتو-زنانه",
        "قهوه-ساز",
    ]
    categories = ProductCategoryModel.objects.filter(slug__in=slugs).only(
        "slug"
    )
    data = {}
    for category in categories:
        data[category.slug] = category

    return {"data": data}


@register.inclusion_tag("includes/best-selling-products.html")
def best_selling_products():
    cached_data = cache.get("best_selling_products")
    if cached_data:
        return {"products": cached_data}

    products = (
        ProductModel.objects.filter(
            status=ProductStatusType.PUBLISH,
            variants__order_items__order__status=OrderStatusType.SUCCESS,
        )
        .prefetch_related(
            "variants",
        )
        .order_by("-total_sold")[:10]
    )

    for product in products:
        variants = list(product.variants.all())
        if variants:
            product.cheapest_variant = min(
                variants, key=lambda v: v.final_price
            )
        else:
            product.cheapest_variant = None

    cache.set("best_selling_products", products, 60 * 60 * 48)
    return {"products": products}


@register.inclusion_tag("includes/posts.html")
def posts():
    return {"posts": PostModel.objects.all().order_by("view_count")[:6]}
