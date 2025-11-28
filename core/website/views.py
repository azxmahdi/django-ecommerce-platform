from django.views.generic import TemplateView
from django.shortcuts import render

from .services.context_builders import IndexContextBuilder


class IndexView(TemplateView):
    template_name = "website/index.html"

    context_builder_class = IndexContextBuilder

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        builder = self.context_builder_class(
            request=self.request, base_context=context_data
        )
        return builder.build()


def custom_page_not_found(request, exception):
    return render(request, "website/404.html", status=404)
