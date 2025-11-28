from django.views.generic import ListView

from .models import FAQCategoryModel
from .services.filters import FAQFilter


class FAQListView(ListView):
    template_name = "faq/list.html"
    context_object_name = "faq_categories"

    filter_class = FAQFilter

    def get_queryset(self):
        base_queryset = FAQCategoryModel.objects.prefetch_related("faqs").all()
        return self.filter_class(self.request.GET).apply(base_queryset)
