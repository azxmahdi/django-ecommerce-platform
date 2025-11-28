from datetime import timedelta
from django.db.models import Count, Q, Subquery, OuterRef, Prefetch
from django.utils.timezone import now


from common.services.base_context_builders import BaseContextBuilder
from order.models import (
    OrderModel,
    OrderStatusType,
    FulfillmentStatus,
    AddressModel,
    OrderItemModel,
)
from wishlist.models import WishlistProductModel
from common.services.pagination_builders import build_pagination_items
from payment.models import PaymentModel


class CounterContextBuilder(BaseContextBuilder):
    def _get_default_processors(self):
        processors = [
            self._add_order_data,
        ]

        return processors

    def get_base_data(self):
        return {}

    def _add_order_data(self):
        all_orders = OrderModel.objects.filter(
            user=self.request.user
        ).order_by("-created_date")
        status_counts = {
            "pending_count": len(
                [o for o in all_orders if o.status == OrderStatusType.PENDING]
            ),
            "success_count": len(
                [o for o in all_orders if o.status == OrderStatusType.SUCCESS]
            ),
            "failed_count": len(
                [o for o in all_orders if o.status == OrderStatusType.FAILED]
            ),
            "delivered_count": len(
                [
                    o
                    for o in all_orders
                    if o.fulfillment_status == FulfillmentStatus.DELIVERED
                ]
            ),
            "returned_count": len(
                [
                    o
                    for o in all_orders
                    if o.fulfillment_status == FulfillmentStatus.RETURNED
                ]
            ),
            "total_count": len(all_orders),
        }
        self.context["wishlists_count"] = WishlistProductModel.objects.filter(
            user=self.request.user
        ).count()
        self.context["status_counts"] = status_counts
        self.context["newest_orders"] = all_orders.filter(
            created_date__gte=now() - timedelta(days=2)
        ).prefetch_related("payment")


class OrderListContextBuilder(BaseContextBuilder):
    def _get_default_processors(self):
        return [
            self._add_order_data,
            self._add_pagination,
        ]

    def get_base_data(self):
        return {}

    from django.db.models import OuterRef, Subquery, Prefetch

    def _add_order_data(self):
        self.context["status_counts"] = OrderModel.objects.filter(
            user=self.request.user
        ).aggregate(
            pending_count=Count(
                "id", filter=Q(status=OrderStatusType.PENDING)
            ),
            success_count=Count(
                "id", filter=Q(status=OrderStatusType.SUCCESS)
            ),
            failed_count=Count("id", filter=Q(status=OrderStatusType.FAILED)),
            delivered_count=Count(
                "id", filter=Q(fulfillment_status=FulfillmentStatus.DELIVERED)
            ),
            returned_count=Count(
                "id", filter=Q(fulfillment_status=FulfillmentStatus.RETURNED)
            ),
            total_count=Count("id"),
        )

        latest_payment_qs = PaymentModel.objects.filter(
            order=OuterRef("pk")
        ).order_by("-created_date")

        pending_orders_qs = (
            OrderModel.objects.filter(
                user=self.request.user, status=OrderStatusType.PENDING
            )
            .select_related("shipping_method", "coupon", "address")
            .prefetch_related(
                Prefetch(
                    "order_items",
                    queryset=OrderItemModel.objects.select_related(
                        "product_variant__product"
                    ),
                )
            )
            .annotate(
                latest_payment_status=Subquery(
                    latest_payment_qs.values("status")[:1]
                ),
                latest_payment_created=Subquery(
                    latest_payment_qs.values("created_date")[:1]
                ),
            )
            .order_by("-created_date")[:5]
        )

        self.context["pending_orders"] = pending_orders_qs

    def _add_pagination(self):
        self.context["page_items"] = build_pagination_items(self.context)

    def _add_pagination(self):
        self.context["page_items"] = build_pagination_items(self.context)


class WishlistProductContextBuilder(BaseContextBuilder):
    def _get_default_processors(self):
        return [
            self._add_pagination,
        ]

    def get_base_data(self):
        return {}

    def _add_pagination(self):
        self.context["page_items"] = build_pagination_items(self.context)


class OrderDetailContextBuilder(BaseContextBuilder):
    def _get_default_processors(self):
        return [
            self._add_addresses,
        ]

    def get_base_data(self):
        return {}

    def _add_addresses(self):
        self.context["addresses"] = AddressModel.objects.filter(
            user=self.request.user
        )


class MessageListContextBuilder(BaseContextBuilder):
    def _get_default_processors(self):
        return [
            self._add_pagination,
        ]

    def get_base_data(self):
        return {}

    def _add_pagination(self):
        self.context["page_items"] = build_pagination_items(self.context)
