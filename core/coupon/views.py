import logging

from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from .services import CouponService
from order.services.order import OrderService
from core.constants import TaskName, LoggerName

apps_logger = logging.getLogger(LoggerName.APPS)


class ApplyCouponView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        code = request.POST.get("code")
        order_id = request.POST.get("order_id")
        if code and order_id:
            status, order = OrderService.try_to_get(order_id)
            if status == "error":
                apps_logger.warning(
                    "Order not found for coupon application",
                    extra={
                        "task_name": TaskName.COUPON_APPLY,
                        "user_id": request.user.id,
                        "order_id": order_id,
                        "coupon_code": code,
                        "correlation_id": getattr(
                            request, "correlation_id", None
                        ),
                    },
                )
                return JsonResponse(
                    {"status": "error", "message": "سفارش یافت نشد"}
                )

            status, message = CouponService.apply_coupon(order, code)
            apps_logger.info(
                "Coupon application result",
                extra={
                    "task_name": TaskName.COUPON_APPLY,
                    "user_id": request.user.id,
                    "order_id": order.id,
                    "coupon_code": code,
                    "status": status,
                    "message": message,
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )
            data = {
                "total_payment_amount": order.get_amount(),
                "total_amount_discounts": request.session[
                    "total_amount_discounts"
                ]
                + order.calculate_discount_coupon(),
            }
            return JsonResponse(
                {"status": status, "message": message, "data": data}
            )

        apps_logger.error(
            "Invalid coupon apply request: missing code or order_id",
            extra={
                "task_name": TaskName.COUPON_APPLY,
                "user_id": request.user.id,
                "order_id": order_id,
                "coupon_code": code,
                "correlation_id": getattr(request, "correlation_id", None),
            },
        )
        return JsonResponse(
            {"status": "error", "message": "اطلاعات کوپن و سفارش ناقص است"}
        )
