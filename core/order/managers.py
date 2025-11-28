from django.db import models
from django.utils import timezone
from datetime import timedelta

from payment.models import PaymentStatusType
from payment.services import PaymentService


class OrderQuerySet(models.QuerySet):
    def with_payment_urls(self):
        now = timezone.now()
        qs = self.select_related("payment__gateway")

        for order in qs:
            payment = getattr(order, "payment", None)
            if (
                payment
                and payment.status == PaymentStatusType.PENDING
                and payment.created_date >= now - timedelta(minutes=11)
            ):
                order.payment_url = PaymentService.generate_url(payment)
            else:
                order.payment_url = None
        return qs

    def filter_by_status_title(self, status_title: str):
        from .models import OrderStatusType, FulfillmentStatus

        try:
            status_title = status_title.upper()

            status_mapping = {
                "PENDING": ("status", OrderStatusType.PENDING),
                "SUCCESS": ("status", OrderStatusType.SUCCESS),
                "FAILED": ("status", OrderStatusType.FAILED),
                "DELIVERED": (
                    "fulfillment_status",
                    FulfillmentStatus.DELIVERED,
                ),
                "RETURNED": ("fulfillment_status", FulfillmentStatus.RETURNED),
            }

            if status_title in status_mapping:
                field_name, status_value = status_mapping[status_title]
                return self.filter(**{field_name: status_value})
            else:
                return self.none()

        except (AttributeError, TypeError):
            return self.none()


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def with_payment_urls(self):
        return self.get_queryset().with_payment_urls()

    def filter_by_status_title(self, status_title: str):
        return self.get_queryset().filter_by_status_title(status_title)
