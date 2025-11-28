import logging

from order.models import OrderModel
from .models import CouponModel
from core.constants import TaskName, LoggerName

apps_logger = logging.getLogger(LoggerName.APPS)


class CouponService:
    @staticmethod
    def apply_coupon(order: OrderModel, coupon_code):
        try:
            coupon = CouponModel.objects.get(code=coupon_code, is_active=True)

            is_valid, message = coupon.validate(order.user)
            if not is_valid:
                apps_logger.warning(
                    "Coupon validation failed",
                    extra={
                        "task_name": TaskName.COUPON_APPLY,
                        "order_id": order.id,
                        "coupon_id": coupon.id,
                        "user_id": order.user.id,
                        "coupon_code": coupon_code,
                        "reason": message,
                    },
                )
                return "error", message

            order.coupon = coupon
            order.save()

            coupon.used_by.add(order.user)
            coupon.save()

            apps_logger.info(
                "Coupon applied successfully",
                extra={
                    "task_name": TaskName.COUPON_APPLY,
                    "order_id": order.id,
                    "coupon_id": coupon.id,
                    "user_id": order.user.id,
                    "coupon_code": coupon_code,
                },
            )

            return "success", message

        except CouponModel.DoesNotExist:
            apps_logger.warning(
                "Coupon not found",
                extra={
                    "task_name": TaskName.COUPON_APPLY,
                    "order_id": order.id,
                    "user_id": order.user.id,
                    "coupon_code": coupon_code,
                },
            )
            return "error", "کوپن یافت نشد"
