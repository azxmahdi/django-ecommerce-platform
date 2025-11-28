from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import PostModel, PostCategoryModel
from blog.services.context_builders import (
    PostListContextBuilder,
    PostDetailContextBuilder,
)
from blog.services.filters import PostFilter


@method_decorator(cache_page(24 * 60 * 60), name="dispatch")
class PostListView(ListView):
    template_name = "blog/post-list.html"
    context_object_name = "posts"
    paginate_by = 12

    filter_class = PostFilter
    context_builder_class = PostListContextBuilder

    def get_queryset(self):
        return self.filter_class(self.request.GET).apply(
            PostModel.objects.all()
        )

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        builder = self.context_builder_class(
            request=self.request,
            base_context=context_data,
        )
        return builder.build()


@method_decorator(cache_page(60 * 60), name="dispatch")
class PostDetailView(DetailView):
    template_name = "blog/post-detail.html"
    queryset = PostModel.objects.filter(
        published_date__lte=timezone.now(), status=True
    ).select_related("author")
    context_object_name = "post"

    context_builder_class = PostDetailContextBuilder

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        builder = self.context_builder_class(
            request=self.request,
            base_context=context_data,
            post=self.get_object(),
        )
        return builder.build()
