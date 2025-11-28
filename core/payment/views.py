import logging

from django.views.generic import FormView, TemplateView, View, DetailView
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models import Q

from order.models import OrderModel, OrderStatusType
from order.services.order import OrderService
from .models import PaymentModel, PaymentGateway, PaymentStatusType
from .forms import GatewaySelectionForm
from .services import PaymentService
from cart.services.cart import CartService
from cart.storage import SessionStorage
from core.constants import TaskName, LoggerName

payment_logger = logging.getLogger(LoggerName.PAYMENT)


class CheckoutPaymentView(LoginRequiredMixin, FormView):
    template_name = "payment/checkout-payment.html"
    form_class = GatewaySelectionForm
    success_url = reverse_lazy("payment:process")

    def dispatch(self, request, *args, **kwargs):
        self.order_id = self.kwargs.get("order_id")
        if not self.order_id:
            payment_logger.warning(
                "CheckoutPaymentView: order_id missing",
                extra={
                    "task_name": TaskName.CHECKOUT_PAYMENT,
                    "user_id": request.user.id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            return redirect("order:checkout-shipping")

        try:
            self.order = OrderModel.objects.get(
                id=self.order_id, user=request.user
            )
            payment_logger.info(
                "CheckoutPaymentView: order retrieved successfully",
                extra={
                    "task_name": TaskName.CHECKOUT_PAYMENT,
                    "user_id": request.user.id,
                    "order_id": self.order_id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
        except OrderModel.DoesNotExist:
            payment_logger.error(
                "CheckoutPaymentView: order not found",
                extra={
                    "task_name": TaskName.CHECKOUT_PAYMENT,
                    "user_id": request.user.id,
                    "order_id": self.order_id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            return redirect("order:checkout-shipping")

        request.session["current_order_id"] = self.order_id

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.request.session["payment_data"] = {
            "gateway": form.cleaned_data["gateway"],
        }
        self.order.total_price = self.order.calculate_total_price()
        self.order.save()
        payment_logger.info(
            "CheckoutPaymentView: payment data stored in session",
            extra={
                "task_name": TaskName.CHECKOUT_PAYMENT,
                "user_id": self.request.user.id,
                "order_id": self.order.id,
                "gateway": form.cleaned_data["gateway"],
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = self.order
        context["gateways"] = PaymentGateway.objects.filter(is_active=True)
        return context


class PaymentProcessView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        payment_data = request.session.get("payment_data")

        if not payment_data:
            payment_logger.error(
                "PaymentProcessView: payment_data missing in session",
                extra={
                    "task_name": TaskName.PAYMENT_PROCESS,
                    "user_id": request.user.id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(request, "اطلاعات پرداخت یافت نشد")
            return redirect(
                reverse(
                    "payment:checkout-payment", kwargs={"pk": payment.order.id}
                )
            )
        order_id = request.session.get("current_order_id")
        if not order_id:
            payment_logger.error(
                "PaymentProcessView: current_order_id missing in session",
                extra={
                    "task_name": TaskName.PAYMENT_PROCESS,
                    "user_id": request.user.id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(request, "سفارش یافت نشد")
            return redirect("order:checkout-shipping")

        try:
            order = (
                OrderModel.objects.filter(id=order_id, user=request.user)
                .exclude(status=OrderStatusType.SUCCESS)
                .get()
            )
            payment_logger.info(
                "PaymentProcessView: order retrieved successfully",
                extra={
                    "task_name": TaskName.PAYMENT_PROCESS,
                    "user_id": request.user.id,
                    "order_id": order_id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
        except OrderModel.DoesNotExist:
            payment_logger.error(
                "PaymentProcessView: order not found",
                extra={
                    "task_name": TaskName.PAYMENT_PROCESS,
                    "user_id": request.user.id,
                    "order_id": order_id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(request, "سفارش معتبر یافت نشد")
            return redirect("order:checkout-shipping")

        payment, error = PaymentService.create_payment(
            gateway=payment_data["gateway"],
            amount=order.get_amount(),
            user=request.user,
            order=order,
        )

        if error:
            payment_logger.error(
                "PaymentProcessView: error creating payment",
                extra={
                    "task_name": TaskName.PAYMENT_PROCESS,
                    "user_id": request.user.id,
                    "order_id": order.id,
                    "error": error,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(request, error)
            return redirect(
                reverse(
                    "payment:checkout-payment", kwargs={"pk": payment.order.id}
                )
            )

        payment_url, authority, error = PaymentService.initiate_payment(
            payment
        )

        if error:
            payment_logger.error(
                "PaymentProcessView: error initiating payment",
                extra={
                    "task_name": TaskName.PAYMENT_PROCESS,
                    "payment_id": payment.id,
                    "order_id": order.id,
                    "error": error,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(request, f"خطا در اتصال به درگاه: {error}")
            return redirect(
                reverse(
                    "payment:checkout-payment", kwargs={"pk": payment.order.id}
                )
            )

        request.session["payment_id"] = str(payment.id)
        request.session["order_id"] = str(order.id)

        if "current_order_id" in request.session:
            del request.session["current_order_id"]

        payment_logger.info(
            "PaymentProcessView: redirecting to payment gateway",
            extra={
                "task_name": TaskName.PAYMENT_PROCESS,
                "payment_id": payment.id,
                "order_id": order.id,
                "authority": authority,
                "payment_url": payment_url,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

        return HttpResponseRedirect(payment_url)


class PaymentSuccessView(LoginRequiredMixin, DetailView):
    template_name = "payment/payment-success.html"
    context_object_name = "payment"

    def get_queryset(self):
        queryset = PaymentModel.objects.filter(
            Q(user=self.request.user) | Q(order__user=self.request.user)
        ).select_related("order")
        payment_logger.info(
            "PaymentSuccessView: queryset retrieved",
            extra={
                "task_name": TaskName.PAYMENT_SUCCESS,
                "user_id": self.request.user.id,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )
        return queryset


class PaymentFailedView(LoginRequiredMixin, DetailView):
    template_name = "payment/payment-failed.html"
    context_object_name = "payment"

    def get_queryset(self):
        queryset = PaymentModel.objects.filter(
            Q(user=self.request.user) | Q(order__user=self.request.user)
        ).select_related("order")
        payment_logger.info(
            "PaymentFailedView: queryset retrieved",
            extra={
                "task_name": TaskName.PAYMENT_FAILED,
                "user_id": self.request.user.id,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )
        return queryset


class PaymentVerifyView(View):

    def get(self, request, *args, **kwargs):
        authority = request.GET.get("Authority")
        status = request.GET.get("Status")

        payment_id = request.session.get("payment_id")
        if payment_id:
            payment = get_object_or_404(PaymentModel, id=payment_id)
            payment_logger.info(
                "PaymentVerifyView: payment retrieved from session",
                extra={
                    "task_name": TaskName.PAYMENT_VERIFY,
                    "payment_id": payment_id,
                    "user_id": request.user.id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )

        else:
            payment = PaymentService.get_payment_by_authority(authority)
            payment_logger.info(
                "PaymentVerifyView: payment retrieved by authority",
                extra={
                    "task_name": TaskName.PAYMENT_VERIFY,
                    "authority": authority,
                    "user_id": request.user.id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
        if not payment:
            payment_logger.error(
                "PaymentVerifyView: payment not found",
                extra={
                    "task_name": TaskName.PAYMENT_VERIFY,
                    "authority": authority,
                    "user_id": request.user.id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(request, "پرداخت یافت نشد")
            return redirect("website:index")

        if status != "OK" or not authority:
            payment.status = PaymentStatusType.FAILED.value
            payment.save()
            OrderService.update_status_after_failed_payment(payment.order)
            payment_logger.warning(
                "PaymentVerifyView: payment failed",
                extra={
                    "task_name": TaskName.PAYMENT_VERIFY,
                    "payment_id": payment.id,
                    "order_id": payment.order.id,
                    "status": status,
                    "authority": authority,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            return redirect(
                reverse("payment:failed", kwargs={"pk": payment.pk})
            )

        success, ref_id, error = PaymentService.verify_payment(payment)

        if "payment_data" in request.session:
            del request.session["payment_data"]
        if "payment_id" in request.session:
            del request.session["payment_id"]

        if success:
            OrderService.update_status_after_success_payment(payment.order)
            payment_logger.info(
                "PaymentVerifyView: payment verified successfully",
                extra={
                    "task_name": TaskName.PAYMENT_VERIFY,
                    "payment_id": payment.id,
                    "order_id": payment.order.id,
                    "ref_id": ref_id,
                    "user_id": request.user.id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            return redirect(
                reverse("payment:success", kwargs={"pk": payment.pk})
            )
        else:
            OrderService.update_status_after_failed_payment(payment.order)
            payment_logger.error(
                "PaymentVerifyView: payment verification failed",
                extra={
                    "task_name": TaskName.PAYMENT_VERIFY,
                    "payment_id": payment.id,
                    "order_id": payment.order.id,
                    "error": error,
                    "user_id": request.user.id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            return redirect(
                reverse("payment:failed", kwargs={"pk": payment.pk})
            )
