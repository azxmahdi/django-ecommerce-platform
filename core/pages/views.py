from django.views.generic import DetailView
from django.shortcuts import get_object_or_404

from .models import StaticPageModel


class StaticPageView(DetailView):
    model = StaticPageModel
    template_name = "pages/static-page.html"
    context_object_name = "page"

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        return get_object_or_404(StaticPageModel, slug=slug, is_active=True)
