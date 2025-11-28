import logging
from django.db import transaction
from django.core.exceptions import ValidationError

from cart.storage import SessionStorage
from cart.services.cart import CartService
from order.models import OrderItemModel, OrderModel, OrderStatusType
from cart.models import CartModel
from core.constants import TaskName, LoggerName

apps_logger = logging.getLogger(LoggerName.APPS)


class StockValidationService:
    @staticmethod
    def validate_stock(items):
        errors = []
        items_to_update = []

        for item in items:
            if item.product_variant.stock < item.quantity:
                if item.product_variant.stock == 0:
                    errors.append(
                        f"محصول {item.product_variant.product.name} موجود نمی‌باشد"
                    )
                    apps_logger.warning(
                        "Product out of stock",
                        extra={
                            "task_name": TaskName.ORDER_VALIDATE_STOCK,
                            "product": item.product_variant.product.name,
                            "requested_quantity": item.quantity,
                            "available_stock": 0,
                        },
                    )
                else:
                    errors.append(
                        f"تعداد درخواستی برای محصول {item.product_variant.product.name} بیشتر از موجودی است. "
                        f"تعداد این محصول در سبد خرید شما به حداکثر موجودی تغییر یافت"
                    )
                    items_to_update.append(
                        {
                            "item": item,
                            "new_quantity": item.product_variant.stock,
                        }
                    )
                    apps_logger.warning(
                        "Requested quantity exceeds stock, will update cart",
                        extra={
                            "task_name": TaskName.ORDER_VALIDATE_STOCK,
                            "product": item.product_variant.product.name,
                            "requested_quantity": item.quantity,
                            "available_stock": item.product_variant.stock,
                            "new_quantity": item.product_variant.stock,
                        },
                    )

        return errors, items_to_update

    @staticmethod
    def update_cart_items(items_to_update, request):
        for item_data in items_to_update:
            cart_item = item_data["item"]
            cart_item.quantity = item_data["new_quantity"]
            cart_item.save()
            CartService(SessionStorage(request.session)).sync(request.user)
            apps_logger.info(
                "Cart item updated due to stock limitation",
                extra={
                    "task_name": TaskName.ORDER_UPDATE_CART_ITEMS,
                    "user_id": request.user.id,
                    "product": cart_item.product_variant.product.name,
                    "new_quantity": item_data["new_quantity"],
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )


class OrderCreationService:
    @staticmethod
    @transaction.atomic
    def create_order_items(order: OrderModel, cart: CartModel):
        for cart_item in cart.cart_items.all():
            cart_item.product_variant.stock -= cart_item.quantity
            cart_item.product_variant.save()
            apps_logger.info(
                "Stock reduced for product",
                extra={
                    "task_name": TaskName.ORDER_CREATE_ITEMS,
                    "order_id": order.id,
                    "user_id": order.user.id,
                    "product": cart_item.product_variant.product.name,
                    "quantity": cart_item.quantity,
                    "remaining_stock": cart_item.product_variant.stock,
                    "correlation_id": getattr(order, "correlation_id", None),
                },
            )
            OrderItemModel.objects.create(
                order=order,
                product_variant=cart_item.product_variant,
                quantity=cart_item.quantity,
                base_price=cart_item.product_variant.price,
                variant_discount_percent=cart_item.product_variant.discount_percent,
            )


class OrderService:
    @staticmethod
    def validate_and_create_order(order: OrderModel, cart: CartModel, request):

        errors, items_to_update = StockValidationService.validate_stock(
            cart.cart_items.all()
        )

        if errors:
            if items_to_update:
                StockValidationService.update_cart_items(
                    items_to_update, request
                )
            apps_logger.error(
                "Order validation failed due to insufficient stock",
                extra={
                    "task_name": TaskName.ORDER_VALIDATE_AND_CREATE,
                    "order_id": order.id,
                    "user_id": order.user.id,
                    "errors": errors,
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )
            raise ValidationError(errors)

        OrderCreationService.create_order_items(order, cart)
        apps_logger.info(
            "Order validated and items created successfully",
            extra={
                "task_name": TaskName.ORDER_VALIDATE_AND_CREATE,
                "order_id": order.id,
                "user_id": order.user.id,
                "items_count": cart.cart_items.count(),
                "correlation_id": getattr(request, "correlation_id", None),
            },
        )
        return True

    @staticmethod
    def try_to_get(order_id):
        order = None
        try:
            order = OrderModel.objects.get(id=order_id)
            apps_logger.info(
                "Order retrieved successfully",
                extra={
                    "task_name": TaskName.ORDER_TRY_GET,
                    "order_id": order.id,
                    "user_id": order.user.id,
                },
            )
            return "success", order
        except OrderModel.DoesNotExist:
            apps_logger.warning(
                "Order not found",
                extra={
                    "task_name": TaskName.ORDER_TRY_GET,
                    "order_id": order_id,
                },
            )
            return "error", order

    @staticmethod
    def update_status_after_success_payment(order: OrderModel):
        order.status = OrderStatusType.SUCCESS
        order.save()
        apps_logger.info(
            "Order status updated to SUCCESS",
            extra={
                "task_name": TaskName.ORDER_UPDATE_STATUS,
                "order_id": order.id,
                "user_id": order.user.id,
                "new_status": OrderStatusType.SUCCESS,
            },
        )

    @staticmethod
    def update_status_after_failed_payment(order: OrderModel):
        order.status = OrderStatusType.FAILED
        order.save()
        apps_logger.warning(
            "Order status updated to FAILED",
            extra={
                "task_name": TaskName.ORDER_UPDATE_STATUS,
                "order_id": order.id,
                "user_id": order.user.id,
                "new_status": OrderStatusType.FAILED,
            },
        )
