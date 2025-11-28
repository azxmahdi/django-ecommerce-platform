from django import template
from django.utils import timezone
from django.db.models import Count

from blog.models import PostModel, PostCategoryModel

register = template.Library()


@register.inclusion_tag("blog/related-posts.html")
def related_posts(categories, exclude_id=None, limit=4):
    queryset = (
        PostModel.objects.filter(
            category__in=categories,
            status=True,
            published_date__lte=timezone.now(),
        )
        .distinct()
        .only("id", "image", "title", "slug", "published_date")
    )
    if exclude_id:
        queryset = queryset.exclude(pk=exclude_id)

    if hasattr(categories, "values_list"):
        slugs_list = list(categories.values_list("slug", flat=True))
    else:
        slugs_list = [getattr(c, "slug", c) for c in categories]

    category_slugs = ",".join(str(slug) for slug in slugs_list if slug)

    return {
        "posts": queryset[:limit],
        "post_count": queryset.count(),
        "category_slugs": category_slugs,
        "limit": limit,
    }


@register.inclusion_tag("blog/popular-posts.html")
def popular_posts(exclude_id=None, limit=3):
    queryset = PostModel.objects.filter(
        status=True, published_date__lte=timezone.now()
    ).order_by("-view_count")
    if exclude_id:
        queryset = queryset.exclude(pk=exclude_id)

    return {"posts": queryset[:limit]}


@register.inclusion_tag("blog/categories.html")
def categories():
    categories = PostCategoryModel.objects.all().annotate(
        post_count=Count("posts")
    )
    return {"categories": categories}
