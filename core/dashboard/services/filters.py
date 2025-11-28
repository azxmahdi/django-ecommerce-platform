from django.db.models import (
    Q,
    Exists,
    OuterRef,
    Subquery,
    ExpressionWrapper,
    DecimalField,
    F,
)
from django.db.models.functions import Round

from common.services.base_filters import BaseFilter
from order.models import OrderStatusType, OrderModel


class OrderFilter(BaseFilter):
    def _get_filter_methods(self):
        return [
            self._filter_by_status,
        ]

    def _filter_by_status(self, queryset):
        if status_title := self.params.get("status"):
            queryset = queryset.filter_by_status_title(status_title)

        return queryset
