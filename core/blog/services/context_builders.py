from django.urls import reverse

from shop.models import (
    ProductCategoryModel,
    CategoryFeatureModel,
    ProductFeatureModel,
)
from blog.models import PostCategoryModel, PostModel
from common.services.pagination_builders import build_pagination_items
from common.services.base_context_builders import BaseContextBuilder


class PostListContextBuilder(BaseContextBuilder):
    def _get_default_processors(self):
        processors = [
            self._add_querystring,
            self._add_categories,
            self._add_pagination,
        ]

        return processors

    def get_base_data(self):
        return {}

    def _add_querystring(self):
        params = self.request.GET.copy()
        params.pop("page", None)
        self.context["querystring"] = params.urlencode()

    def _add_categories(self):
        self.context["post_categories"] = PostCategoryModel.objects.all()

    def _add_pagination(self):
        self.context["page_items"] = build_pagination_items(self.context)


class PostDetailContextBuilder(BaseContextBuilder):
    def _get_default_processors(self):
        return [
            self._add_absolute_url,
        ]

    def get_base_data(self):
        return {}

    def _add_absolute_url(self):
        post = self.extra_data.get("post")
        if post:
            self.context["absolute_url"] = self.request.build_absolute_uri(
                reverse("blog:post-detail", args=[post.pk])
            )
