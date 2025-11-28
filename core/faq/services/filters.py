from django.db.models import Q

from common.services.base_filters import BaseFilter


class FAQFilter(BaseFilter):
    def _get_filter_methods(self):
        return [
            self._filter_by_search,
        ]

    def _filter_by_search(self, queryset):
        if q := self.params.get("q"):
            queryset = queryset.filter(
                Q(faqs__question__icontains=q) | Q(faqs__answer__icontains=q)
            )
        return queryset
