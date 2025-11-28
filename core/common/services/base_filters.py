from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable
from django.db.models import QuerySet


class BaseFilter(ABC):
    def __init__(self, params: Dict[str, Any]):
        self.params = params
        self._custom_filters: List[Callable] = []

    def apply(self, queryset: QuerySet) -> QuerySet:

        filter_methods = self._get_filter_methods() + self._custom_filters

        for filter_method in filter_methods:
            queryset = filter_method(queryset)

        return queryset

    def add_custom_filter(self, filter_func: Callable):
        self._custom_filters.append(filter_func)
        return self

    @abstractmethod
    def _get_filter_methods(self) -> List[Callable]:
        pass
